from flask import Flask, render_template, request

import db
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

STATUSES = ["Upcoming", "In_progress", "Completed", "Cancelled"]
STYLING_AIDS = ["None", "Moustache_only", "Allowed"]


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


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", message="Page not found."), 404


if __name__ == "__main__":
    app.run(debug=True, port=5001)