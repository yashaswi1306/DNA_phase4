import pymysql
import pymysql.cursors

from config import get_db_config


def get_connection():
    return pymysql.connect(**get_db_config(), cursorclass=pymysql.cursors.DictCursor)


def fetch_all(sql, params=()):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def fetch_one(sql, params=()):
    rows = fetch_all(sql, params)
    if rows:
        return rows[0]
    return None


# Query 1: search competitors by name (also checks other spellings in PERSON_ALIAS)
def search_competitors(name):
    sql = """
        SELECT p.Person_ID, p.Display_Name, p.Hometown_City, p.Hometown_Country
        FROM PERSON p
        JOIN COMPETITOR c ON c.Person_ID = p.Person_ID
        WHERE p.Display_Name LIKE %s
           OR p.Person_ID IN (SELECT Person_ID FROM PERSON_ALIAS WHERE Alias LIKE %s)
        ORDER BY p.Display_Name
    """
    pattern = "%" + name + "%"
    return fetch_all(sql, (pattern, pattern))


# Query 2: list championships, filtered by status and by styling aids rule
def get_championships(status=None, styling_aids=None):
    sql = """
        SELECT ch.Champ_ID, ch.Year, ch.Host_City, ch.Host_Country, ch.Status,
               cl.Name AS Host_Club,
               COUNT(DISTINCT o.Category_ID) AS Num_Categories
        FROM CHAMPIONSHIP ch
        LEFT JOIN CLUB cl ON cl.Club_ID = ch.Host_Club_ID
        LEFT JOIN OFFERS o ON o.Champ_ID = ch.Champ_ID
        WHERE (%s IS NULL OR ch.Status = %s)
          AND (%s IS NULL OR o.Styling_Aids = %s)
        GROUP BY ch.Champ_ID, ch.Year, ch.Host_City, ch.Host_Country, ch.Status, cl.Name
        ORDER BY ch.Year DESC
    """
    return fetch_all(sql, (status, status, styling_aids, styling_aids))


# Query 3: one championship with venue, host club, event dates and the edition it replaced
def get_championship(champ_id):
    sql = """
        SELECT ch.Champ_ID, ch.Year, ch.Host_City, ch.Host_Region, ch.Host_Country, ch.Status,
               ch.Max_Categories_Per_Competitor,
               v.Name AS Venue, v.Street AS Venue_Street,
               cl.Name AS Host_Club,
               r.Year AS Replaces_Year,
               GROUP_CONCAT(ed.Event_Date ORDER BY ed.Event_Date SEPARATOR ', ') AS Event_Dates
        FROM CHAMPIONSHIP ch
        LEFT JOIN VENUE v ON v.Venue_ID = ch.Venue_ID
        LEFT JOIN CLUB cl ON cl.Club_ID = ch.Host_Club_ID
        LEFT JOIN CHAMPIONSHIP r ON r.Champ_ID = ch.Replaces_Champ_ID
        LEFT JOIN CHAMP_EVENT_DATE ed ON ed.Champ_ID = ch.Champ_ID
        WHERE ch.Champ_ID = %s
        GROUP BY ch.Champ_ID, ch.Year, ch.Host_City, ch.Host_Region, ch.Host_Country, ch.Status,
                 ch.Max_Categories_Per_Competitor, v.Name, v.Street, cl.Name, r.Year
    """
    return fetch_one(sql, (champ_id,))


def get_charities(champ_id):
    sql = """
        SELECT c.Name
        FROM SUPPORTS s
        JOIN CHARITY c ON c.Charity_ID = s.Charity_ID
        WHERE s.Champ_ID = %s
    """
    return fetch_all(sql, (champ_id,))


def get_best_in_show(champ_id):
    sql = """
        SELECT b.Division, p.Person_ID, p.Display_Name
        FROM BEST_IN_SHOW b
        JOIN PERSON p ON p.Person_ID = b.Person_ID
        WHERE b.Champ_ID = %s
    """
    return fetch_all(sql, (champ_id,))


# categories offered at a championship (for the dropdown on the results page)
def get_categories(champ_id):
    sql = """
        SELECT Category_ID, Display_Name, Category_Group
        FROM OFFERS
        WHERE Champ_ID = %s
        ORDER BY Category_Group, Display_Name
    """
    return fetch_all(sql, (champ_id,))


# Query 4: results of a championship, optionally for one category
def get_results(champ_id, category_id=None):
    sql = """
        SELECT o.Category_Group, o.Display_Name AS Category, ci.Placement, ci.Score,
               p.Person_ID, p.Display_Name,
               cae.Event_Hometown_City, cae.Event_Hometown_Country
        FROM COMPETES_IN ci
        JOIN PERSON p ON p.Person_ID = ci.Person_ID
        JOIN OFFERS o ON o.Champ_ID = ci.Champ_ID AND o.Category_ID = ci.Category_ID
        LEFT JOIN COMPETITOR_AT_EDITION cae ON cae.Person_ID = ci.Person_ID AND cae.Champ_ID = ci.Champ_ID
        WHERE ci.Champ_ID = %s
          AND ci.Placement IS NOT NULL
          AND (%s IS NULL OR ci.Category_ID = %s)
        ORDER BY o.Category_Group, o.Display_Name, ci.Placement
    """
    return fetch_all(sql, (champ_id, category_id, category_id))


# Query 5: competitor profile
def get_competitor(person_id):
    sql = """
        SELECT p.Person_ID, p.Display_Name, p.Nickname,
               p.Hometown_City, p.Hometown_Region, p.Hometown_Country
        FROM PERSON p
        JOIN COMPETITOR c ON c.Person_ID = p.Person_ID
        WHERE p.Person_ID = %s
    """
    return fetch_one(sql, (person_id,))


def get_competitor_history(person_id):
    sql = """
        SELECT ch.Champ_ID, ch.Year, ch.Host_City, o.Display_Name AS Category,
               cae.Represented_Country, ci.Placement, ci.Score, ci.Entry_Status
        FROM COMPETES_IN ci
        JOIN CHAMPIONSHIP ch ON ch.Champ_ID = ci.Champ_ID
        JOIN OFFERS o ON o.Champ_ID = ci.Champ_ID AND o.Category_ID = ci.Category_ID
        LEFT JOIN COMPETITOR_AT_EDITION cae ON cae.Person_ID = ci.Person_ID AND cae.Champ_ID = ci.Champ_ID
        WHERE ci.Person_ID = %s
        ORDER BY ch.Year DESC
    """
    return fetch_all(sql, (person_id,))


def get_competitor_clubs(person_id):
    sql = """
        SELECT cl.Name, cl.Country
        FROM MEMBER_OF m
        JOIN CLUB cl ON cl.Club_ID = m.Club_ID
        WHERE m.Person_ID = %s
    """
    return fetch_all(sql, (person_id,))


def get_competitor_awards(person_id):
    sql = """
        SELECT ch.Champ_ID, ch.Year, ch.Host_City, b.Division
        FROM BEST_IN_SHOW b
        JOIN CHAMPIONSHIP ch ON ch.Champ_ID = b.Champ_ID
        WHERE b.Person_ID = %s
        ORDER BY ch.Year DESC
    """
    return fetch_all(sql, (person_id,))