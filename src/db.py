#Database access layer

#All database operations use native, parameterised SQL.
#No ORM or query builder is used.

from contextlib import contextmanager
from datetime import date

import pymysql
from pymysql.cursors import DictCursor

from config import get_db_config

# when a requested database record does not exist
class NotFoundError(Exception):
    pass

# when submitted data is invalid
class ValidationError(Exception):
    pass


@contextmanager
#Open a database connection and always close it
def connection():

    conn = pymysql.connect(
        **get_db_config(),
        cursorclass=DictCursor,
        autocommit=False
    )

    try:
        yield conn
    finally:
        conn.close()


# READ 1: Search competitors by display name

def search_competitors(query):

    sql = """
        SELECT
            p.Person_ID,
            p.Display_Name,
            p.Hometown_City,
            p.Hometown_Country

        FROM PERSON AS p

        INNER JOIN COMPETITOR AS c
            ON c.Person_ID = p.Person_ID

        WHERE p.Display_Name LIKE %s

        ORDER BY p.Display_Name

        LIMIT 100
    """

    with connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                sql,
                (f"%{query}%",)
            )

            return cur.fetchall()


# READ 2: Filter championships by status and styling aids

def filter_championships(status=None, styling_aids=None):

    allowed_statuses = {
        "Upcoming",
        "In_progress",
        "Completed",
        "Cancelled"
    }

    allowed_aids = {
        "None",
        "Moustache_only",
        "Allowed"
    }

    if status and status not in allowed_statuses:
        raise ValidationError(
            "Invalid championship status."
        )

    if styling_aids and styling_aids not in allowed_aids:
        raise ValidationError(
            "Invalid styling-aids filter."
        )

    sql = """
        SELECT
            ch.Champ_ID,
            ch.Year,
            ch.Host_City,
            ch.Host_Region,
            ch.Host_Country,
            ch.Status,

            GROUP_CONCAT(
                DISTINCT o.Display_Name
                ORDER BY o.Display_Name
                SEPARATOR ', '
            ) AS Categories

        FROM CHAMPIONSHIP AS ch

        LEFT JOIN OFFERS AS o
            ON o.Champ_ID = ch.Champ_ID

        WHERE
            (%s IS NULL OR ch.Status = %s)
            AND
            (%s IS NULL OR o.Styling_Aids = %s)

        GROUP BY
            ch.Champ_ID,
            ch.Year,
            ch.Host_City,
            ch.Host_Region,
            ch.Host_Country,
            ch.Status

        ORDER BY ch.Year DESC
    """

    with connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                sql,
                (
                    status,
                    status,
                    styling_aids,
                    styling_aids
                )
            )

            return cur.fetchall()


# READ 3: Championship details (joins CHAMPIONSHIP, VENUE, CLUB and CHAMP_EVENT_DATE)

def get_championship_details(champ_id):

    sql = """
        SELECT
            ch.Champ_ID,
            ch.Year,
            ch.Host_City,
            ch.Host_Region,
            ch.Host_Country,
            ch.Status,
            ch.Registration_Opens,
            ch.Registration_Closes,
            ch.Max_Categories_Per_Competitor,

            v.Name AS Venue_Name,
            v.Street AS Venue_Street,
            v.City AS Venue_City,
            v.Region AS Venue_Region,
            v.Country AS Venue_Country,

            cl.Name AS Host_Club,

            GROUP_CONCAT(
                DATE_FORMAT(ed.Event_Date, '%%Y-%%m-%%d')
                ORDER BY ed.Event_Date
                SEPARATOR ', '
            ) AS Event_Dates

        FROM CHAMPIONSHIP AS ch

        LEFT JOIN VENUE AS v
            ON v.Venue_ID = ch.Venue_ID

        LEFT JOIN CLUB AS cl
            ON cl.Club_ID = ch.Host_Club_ID

        LEFT JOIN CHAMP_EVENT_DATE AS ed
            ON ed.Champ_ID = ch.Champ_ID

        WHERE ch.Champ_ID = %s

        GROUP BY
            ch.Champ_ID,
            ch.Year,
            ch.Host_City,
            ch.Host_Region,
            ch.Host_Country,
            ch.Status,
            ch.Registration_Opens,
            ch.Registration_Closes,
            ch.Max_Categories_Per_Competitor,
            v.Name,
            v.Street,
            v.City,
            v.Region,
            v.Country,
            cl.Name
    """

    with connection() as conn:

        with conn.cursor() as cur:

            cur.execute(sql, (champ_id,))

            row = cur.fetchone()

            if row is None:
                raise NotFoundError(
                    "Championship not found."
                )

            return row


# READ 4: Leaderboard for a championship

def get_leaderboard(champ_id, category_id=None):

    sql = """
        SELECT
            ci.Champ_ID,
            ci.Category_ID,
            cat.Name AS Category_Name,
            ci.Placement,
            ci.Score,
            ci.Competitor_No,
            p.Person_ID,
            p.Display_Name,
            ci.Beard_Length_cm

        FROM COMPETES_IN AS ci

        INNER JOIN PERSON AS p
            ON p.Person_ID = ci.Person_ID

        INNER JOIN CATEGORY AS cat
            ON cat.Category_ID = ci.Category_ID

        WHERE
            ci.Champ_ID = %s
            AND ci.Score IS NOT NULL
            AND (
                %s IS NULL
                OR ci.Category_ID = %s
            )

        ORDER BY
            ci.Category_ID,
            ci.Placement IS NULL,
            ci.Placement ASC,
            ci.Score DESC,
            p.Display_Name
    """

    with connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                sql,
                (
                    champ_id,
                    category_id,
                    category_id
                )
            )

            return cur.fetchall()


# READ 5: Competitor profile (includes clubs, event history and awards)

def get_competitor_profile(person_id):

    profile_sql = """
        SELECT
            p.Person_ID,
            p.Display_Name,
            p.Given_Name,
            p.Family_Name,
            p.Nickname,
            p.Date_of_Birth,
            p.Hometown_City,
            p.Hometown_Region,
            p.Hometown_Country

        FROM PERSON AS p

        INNER JOIN COMPETITOR AS c
            ON c.Person_ID = p.Person_ID

        WHERE p.Person_ID = %s
    """

    clubs_sql = """
        SELECT
            cl.Club_ID,
            cl.Name,
            cl.Country,
            cl.Membership_Status

        FROM MEMBER_OF AS mo

        INNER JOIN CLUB AS cl
            ON cl.Club_ID = mo.Club_ID

        WHERE mo.Person_ID = %s

        ORDER BY cl.Name
    """

    history_sql = """
        SELECT
            ch.Champ_ID,
            ch.Year,
            ch.Host_City,
            ch.Status,
            cat.Name AS Category_Name,
            ci.Competitor_No,
            ci.Score,
            ci.Placement,
            ci.Entry_Status

        FROM COMPETES_IN AS ci

        INNER JOIN CHAMPIONSHIP AS ch
            ON ch.Champ_ID = ci.Champ_ID

        INNER JOIN CATEGORY AS cat
            ON cat.Category_ID = ci.Category_ID

        WHERE ci.Person_ID = %s

        ORDER BY
            ch.Year DESC,
            cat.Name
    """

    awards_sql = """
        SELECT
            bis.Champ_ID,
            ch.Year,
            bis.Division

        FROM BEST_IN_SHOW AS bis

        INNER JOIN CHAMPIONSHIP AS ch
            ON ch.Champ_ID = bis.Champ_ID

        WHERE bis.Person_ID = %s

        ORDER BY ch.Year DESC
    """

    with connection() as conn:

        with conn.cursor() as cur:

            # Basic competitor information
            cur.execute(
                profile_sql,
                (person_id,)
            )

            profile = cur.fetchone()

            if profile is None:
                raise NotFoundError(
                    "Competitor not found."
                )

            # Club memberships
            cur.execute(
                clubs_sql,
                (person_id,)
            )

            profile["clubs"] = cur.fetchall()

            # Championship participation
            cur.execute(
                history_sql,
                (person_id,)
            )

            profile["event_history"] = cur.fetchall()

            # Best in Show awards
            cur.execute(
                awards_sql,
                (person_id,)
            )

            profile["best_in_show_awards"] = cur.fetchall()

            return profile


# Create a spectator/competitor ticket

def create_ticket(
    champ_id,
    holder_id,
    ticket_type,
    access,
    price,
    currency,
    valid_on=None
):

    allowed_types = {
        "Competitor",
        "Spectator",
        "Kids_competitor",
        "Kids_spectator"
    }

    if ticket_type not in allowed_types:
        raise ValidationError(
            "Invalid ticket type."
        )

    if access not in {"Day", "Weekend"}:
        raise ValidationError(
            "Access must be Day or Weekend."
        )

    if access == "Day" and not valid_on:
        raise ValidationError(
            "A Day ticket requires an event date."
        )

    if access == "Weekend" and valid_on:
        raise ValidationError(
            "A Weekend ticket must not have a single valid-on date."
        )

    try:
        price = float(price)

    except (TypeError, ValueError):
        raise ValidationError(
            "Price must be a non-negative number."
        )

    if price < 0:
        raise ValidationError(
            "Price must be non-negative."
        )

    if valid_on is not None:

        try:
            valid_on = date.fromisoformat(
                str(valid_on)
            ).isoformat()

        except ValueError:
            raise ValidationError(
                "valid_on must be a date in YYYY-MM-DD format."
            )

    currency = str(currency).upper().strip()

    if len(currency) != 3 or not currency.isalpha():
        raise ValidationError(
            "Currency must be a 3-letter code, such as USD."
        )

    with connection() as conn:

        try:

            with conn.cursor() as cur:

                # Lock the championship row while allocating
                # the next ticket number.
                cur.execute(
                    """
                    SELECT Champ_ID
                    FROM CHAMPIONSHIP
                    WHERE Champ_ID = %s
                    FOR UPDATE
                    """,
                    (champ_id,)
                )

                if cur.fetchone() is None:
                    raise NotFoundError(
                        "Championship not found."
                    )

                # Verify that the ticket holder exists.
                cur.execute(
                    """
                    SELECT Person_ID
                    FROM PERSON
                    WHERE Person_ID = %s
                    """,
                    (holder_id,)
                )

                if cur.fetchone() is None:
                    raise NotFoundError(
                        "Ticket holder not found."
                    )

                # A Day ticket must refer to an actual
                # event date belonging to this championship.
                if access == "Day":

                    cur.execute(
                        """
                        SELECT Event_Date
                        FROM CHAMP_EVENT_DATE
                        WHERE Champ_ID = %s
                        AND Event_Date = %s
                        """,
                        (champ_id, valid_on)
                    )

                    if cur.fetchone() is None:
                        raise ValidationError(
                            "The selected date is not an event date "
                            "for this championship."
                        )

                # Allocate the next ticket number.
                cur.execute(
                    """
                    SELECT COALESCE(MAX(Ticket_No), 0) + 1
                        AS next_no
                    FROM TICKET
                    WHERE Champ_ID = %s
                    """,
                    (champ_id,)
                )

                ticket_no = cur.fetchone()["next_no"]

                # Insert ticket.
                cur.execute(
                    """
                    INSERT INTO TICKET (
                        Champ_ID,
                        Ticket_No,
                        Type,
                        Access,
                        Price,
                        Currency,
                        Status,
                        Valid_On,
                        Holder_ID
                    )

                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, 'Valid', %s, %s
                    )
                    """,
                    (
                        champ_id,
                        ticket_no,
                        ticket_type,
                        access,
                        price,
                        currency,
                        valid_on,
                        holder_id
                    )
                )

            conn.commit()

            return {
                "Champ_ID": champ_id,
                "Ticket_No": ticket_no,
                "Type": ticket_type,
                "Access": access,
                "Price": price,
                "Currency": currency,
                "Status": "Valid",
                "Valid_On": valid_on,
                "Holder_ID": holder_id
            }

        except Exception:

            conn.rollback()
            raise


# Check in a competitor

def check_in_competitor(
    person_id,
    category_id,
    champ_id
):

    sql = """
        UPDATE COMPETES_IN

        SET
            Checked_In = TRUE,
            Check_In_At = CURRENT_TIMESTAMP,
            Entry_Status = 'Checked_in'

        WHERE
            Person_ID = %s
            AND Category_ID = %s
            AND Champ_ID = %s
            AND Checked_In = FALSE
            AND Entry_Status = 'Registered'
    """

    with connection() as conn:

        try:

            with conn.cursor() as cur:

                cur.execute(
                    sql,
                    (
                        person_id,
                        category_id,
                        champ_id
                    )
                )

                if cur.rowcount == 0:

                    cur.execute(
                        """
                        SELECT
                            Checked_In,
                            Entry_Status

                        FROM COMPETES_IN

                        WHERE
                            Person_ID = %s
                            AND Category_ID = %s
                            AND Champ_ID = %s
                        """,
                        (
                            person_id,
                            category_id,
                            champ_id
                        )
                    )

                    row = cur.fetchone()

                    if row is None:
                        raise NotFoundError(
                            "Competitor entry not found."
                        )

                    raise ValidationError(
                        "This entry is not eligible for check-in. "
                        "It may already be checked in or no longer registered."
                    )

                # Retrieve the updated record.
                cur.execute(
                    """
                    SELECT
                        Person_ID,
                        Category_ID,
                        Champ_ID,
                        Competitor_No,
                        Checked_In,
                        Check_In_At,
                        Entry_Status

                    FROM COMPETES_IN

                    WHERE
                        Person_ID = %s
                        AND Category_ID = %s
                        AND Champ_ID = %s
                    """,
                    (
                        person_id,
                        category_id,
                        champ_id
                    )
                )

                result = cur.fetchone()

            conn.commit()

            return result

        except Exception:

            conn.rollback()
            raise


# Delete a ticket

def delete_ticket(champ_id, ticket_no):

    sql = """
        DELETE FROM TICKET

        WHERE
            Champ_ID = %s
            AND Ticket_No = %s
    """

    with connection() as conn:

        try:

            with conn.cursor() as cur:

                cur.execute(
                    sql,
                    (champ_id, ticket_no)
                )

                if cur.rowcount == 0:
                    raise NotFoundError(
                        "Ticket not found."
                    )

            conn.commit()

            return {
                "Champ_ID": champ_id,
                "Ticket_No": ticket_no,
                "deleted": True
            }

        except Exception:

            conn.rollback()
            raise
