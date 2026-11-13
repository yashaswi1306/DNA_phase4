import pymysql
from flask import Flask, flash, redirect, render_template, request

import db
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

STATUSES = ["Upcoming", "In_progress", "Completed", "Cancelled"]
STYLING_AIDS = ["None", "Moustache_only", "Allowed"]
TICKET_TYPES = ["Spectator", "Competitor", "Kids_spectator", "Kids_competitor"]


@app.route("/")
def index():
    status = request.args.get("status") or None
    styling_aids = request.args.get("styling_aids") or None
    error = None

    if status is not None and status not in STATUSES:
        error = "Invalid status."
        status = None
    if styling_aids is not None and styling_aids not in STYLING_AIDS:
        error = "Invalid styling aids value."
        styling_aids = None

    championships = db.get_championships(status, styling_aids)
    return render_template("index.html", championships=championships, status=status,
                           styling_aids=styling_aids, statuses=STATUSES,
                           styling_options=STYLING_AIDS, error=error)


@app.route("/championship/<int:champ_id>")
def championship(champ_id):
    champ = db.get_championship(champ_id)
    if champ is None:
        return render_template("error.html", message="Championship not found."), 404

    category_id = request.args.get("category", type=int)
    results = db.get_results(champ_id, category_id)
    return render_template("championship.html", champ=champ, results=results,
                           categories=db.get_categories(champ_id),
                           category_id=category_id,
                           charities=db.get_charities(champ_id),
                           best_in_show=db.get_best_in_show(champ_id))


@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    people = []
    if q:
        people = db.search_competitors(q)
    return render_template("search.html", q=q, people=people)


@app.route("/competitor/<int:person_id>")
def competitor(person_id):
    person = db.get_competitor(person_id)
    if person is None:
        return render_template("error.html", message="Competitor not found."), 404

    return render_template("competitor.html", person=person,
                           history=db.get_competitor_history(person_id),
                           clubs=db.get_competitor_clubs(person_id),
                           awards=db.get_competitor_awards(person_id))


# picks the championship from ?champ_id=, otherwise the first upcoming one
def selected_championship(championships):
    champ_id = request.args.get("champ_id", type=int)
    for c in championships:
        if c["Champ_ID"] == champ_id:
            return c
    for c in championships:
        if c["Status"] == "Upcoming":
            return c
    return championships[0]


@app.route("/tickets")
def tickets():
    championships = db.get_championships()
    champ = selected_championship(championships)
    return render_template("tickets.html", championships=championships, champ=champ,
                           tickets=db.get_tickets(champ["Champ_ID"]),
                           people=db.get_people(),
                           dates=db.get_event_dates(champ["Champ_ID"]),
                           ticket_types=TICKET_TYPES)


@app.route("/tickets/new", methods=["POST"])
def new_ticket():
    champ_id = request.form.get("champ_id", type=int)
    holder_id = request.form.get("holder_id", type=int)
    ticket_type = request.form.get("type")
    access = request.form.get("access")
    valid_on = request.form.get("valid_on") or None
    currency = request.form.get("currency", "").strip().upper()

    try:
        price = float(request.form.get("price", ""))
    except ValueError:
        price = None

    if holder_id is None:
        flash("Choose a ticket holder.", "error")
    elif ticket_type not in TICKET_TYPES or access not in ("Day", "Weekend"):
        flash("Invalid ticket type or access.", "error")
    elif price is None or price < 0:
        flash("Price must be a number that is 0 or more.", "error")
    elif len(currency) != 3:
        flash("Currency must be a 3 letter code like GBP.", "error")
    elif access == "Day" and valid_on is None:
        flash("A Day ticket needs a date.", "error")
    else:
        if access == "Weekend":
            valid_on = None
        try:
            ticket_no = db.create_ticket(champ_id, holder_id, ticket_type, access, price, currency, valid_on)
            flash("Ticket " + str(ticket_no) + " created.", "success")
        except ValueError as e:
            flash(str(e), "error")
        except pymysql.MySQLError as e:
            flash("Database error: " + str(e.args[-1]), "error")

    return redirect("/tickets?champ_id=" + str(champ_id))


@app.route("/tickets/delete", methods=["POST"])
def delete_ticket():
    champ_id = request.form.get("champ_id", type=int)
    ticket_no = request.form.get("ticket_no", type=int)

    try:
        if db.delete_ticket(champ_id, ticket_no) == 0:
            flash("Ticket not found.", "error")
        else:
            flash("Ticket " + str(ticket_no) + " deleted.", "success")
    except pymysql.MySQLError as e:
        flash("Database error: " + str(e.args[-1]), "error")

    return redirect("/tickets?champ_id=" + str(champ_id))


@app.route("/checkin")
def checkin():
    championships = db.get_championships()
    champ = selected_championship(championships)
    return render_template("checkin.html", championships=championships, champ=champ,
                           entries=db.get_registered_entries(champ["Champ_ID"]))


@app.route("/checkin", methods=["POST"])
def do_checkin():
    person_id = request.form.get("person_id", type=int)
    category_id = request.form.get("category_id", type=int)
    champ_id = request.form.get("champ_id", type=int)

    try:
        if db.check_in(person_id, category_id, champ_id) == 0:
            flash("This competitor is not registered or is already checked in.", "error")
        else:
            flash("Competitor checked in.", "success")
    except pymysql.MySQLError as e:
        flash("Database error: " + str(e.args[-1]), "error")

    return redirect("/checkin?champ_id=" + str(champ_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", message="Page not found."), 404


if __name__ == "__main__":
    app.run(debug=True, port=5001)