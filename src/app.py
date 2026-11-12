#Flask AP

#The frontend communicates with this backend through JSON endpoints.
#All database operations are handled by db.py.

from decimal import Decimal
from datetime import date, datetime

import pymysql

from flask import Flask, jsonify, request

import db
from config import SECRET_KEY


app = Flask(__name__)
app.secret_key = SECRET_KEY


# json serialisation

def json_safe(value):
    #Convert database values into JSON-compatible values

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, dict):
        return {
            key: json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            json_safe(item)
            for item in value
        ]

    return value


def success(data, status=200):
    #Return a successful JSON response

    return jsonify({
        "ok": True,
        "data": json_safe(data)
    }), status


def bad_request(message, status=400):
    #Return an error JSON response

    return jsonify({
        "ok": False,
        "error": message
    }), status


# home and heath ticket

@app.get("/")
def index():

    return jsonify({
        "message": "WBMC Phase 4 API",
        "health": "/health",

        "endpoints": [
            "/api/competitors?q=",
            "/api/championships",
            "/api/championships/<champ_id>",
            "/api/leaderboard",
            "/api/competitors/<person_id>",
            "/api/tickets",
            "/api/competitions/check-in",
            "/api/tickets/<champ_id>/<ticket_no>"
        ]
    })


@app.get("/health")
def health():

    return success({
        "status": "running"
    })


# READ 1: search competitors
# GET /api/competitors?q=Bryan

@app.get("/api/competitors")
def api_search_competitors():

    query = request.args.get(
        "q", ""
    ).strip()

    if not query:
        return bad_request(
            "Provide a non-empty q search term."
        )

    return success(
        db.search_competitors(query)
    )


# READ 2: filter championship
# GET /api/championships?status=Completed

@app.get("/api/championships")
def api_filter_championships():

    try:

        status = request.args.get(
            "status"
        ) or None

        styling_aids = request.args.get(
            "styling_aids"
        ) or None

        results = db.filter_championships(
            status,
            styling_aids
        )

        return success(results)

    except db.ValidationError as exc:

        return bad_request(str(exc))


# READ 3: championship details
# GET /api/championships/4

@app.get("/api/championships/<int:champ_id>")
def api_championship_details(champ_id):

    try:

        result = db.get_championship_details(
            champ_id
        )

        return success(result)

    except db.NotFoundError as exc:

        return bad_request(
            str(exc),
            404
        )


# READ 4: leaderboard
# GET /api/leaderboard?champ_id=4&category_id=14

@app.get("/api/leaderboard")
def api_leaderboard():

    champ_id = request.args.get(
        "champ_id",
        type=int
    )

    category_id = request.args.get(
        "category_id",
        type=int
    )

    if champ_id is None or champ_id <= 0:
        return bad_request(
            "champ_id must be a positive integer."
        )

    if category_id is not None and category_id <= 0:
        return bad_request(
            "category_id must be a positive integer."
        )

    return success(
        db.get_leaderboard(
            champ_id,
            category_id
        )
    )


# READ 5: competitor profile
# GET /api/competitors/16

@app.get("/api/competitors/<int:person_id>")
def api_competitor_profile(person_id):

    try:

        result = db.get_competitor_profile(
            person_id
        )

        return success(result)

    except db.NotFoundError as exc:

        return bad_request(
            str(exc),
            404
        )


# CREATE 6: create ticket
# POST /api/tickets

@app.post("/api/tickets")
def api_create_ticket():

    payload = request.get_json(
        silent=True
    ) or {}

    required = (
        "champ_id",
        "holder_id",
        "type",
        "access",
        "price",
        "currency"
    )

    missing = [
        key
        for key in required
        if payload.get(key) in (None, "")
    ]

    if missing:
        return bad_request(
            "Missing required fields: "
            + ", ".join(missing)
        )

    try:

        champ_id = int(payload["champ_id"])
        holder_id = int(payload["holder_id"])

        if champ_id <= 0 or holder_id <= 0:
            raise ValueError

    except (TypeError, ValueError):

        return bad_request(
            "champ_id and holder_id must be positive integers."
        )

    try:

        created = db.create_ticket(
            champ_id,
            holder_id,
            payload["type"],
            payload["access"],
            payload["price"],
            payload["currency"],
            payload.get("valid_on") or None
        )

        return success(
            created,
            201
        )

    except db.ValidationError as exc:

        return bad_request(str(exc))

    except db.NotFoundError as exc:

        return bad_request(
            str(exc),
            404
        )


# competitor check-in
# POST /api/competitions/check-in

@app.post("/api/competitions/check-in")
def api_check_in():

    payload = request.get_json(
        silent=True
    ) or {}

    try:

        person_id = int(
            payload["person_id"]
        )

        category_id = int(
            payload["category_id"]
        )

        champ_id = int(
            payload["champ_id"]
        )

        if min(
            person_id,
            category_id,
            champ_id
        ) <= 0:
            raise ValueError

    except (KeyError, TypeError, ValueError):

        return bad_request(
            "person_id, category_id and champ_id "
            "must be positive integers."
        )

    try:

        result = db.check_in_competitor(
            person_id,
            category_id,
            champ_id
        )

        return success(result)

    except db.NotFoundError as exc:

        return bad_request(
            str(exc),
            404
        )

    except db.ValidationError as exc:

        return bad_request(
            str(exc),
            409
        )


# delete ticket
# DELETE /api/tickets/4/999

@app.delete(
    "/api/tickets/<int:champ_id>/<int:ticket_no>"
)
def api_delete_ticket(champ_id, ticket_no):

    try:

        result = db.delete_ticket(
            champ_id,
            ticket_no
        )

        return success(result)

    except db.NotFoundError as exc:

        return bad_request(
            str(exc),
            404
        )

    except pymysql.IntegrityError:

        return bad_request(
            "This ticket cannot be deleted because "
            "another record depends on it.",
            409
        )


# global error handlers

@app.errorhandler(pymysql.MySQLError)
def handle_database_error(error):

    # Do not expose SQL queries, credentials or internal database details to the frontend.

    app.logger.exception(
        "Database operation failed"
    )

    return bad_request(
        "A database operation failed. "
        "Check the submitted values and database constraints.",
        500
    )


@app.errorhandler(404)
def handle_route_not_found(error):

    return bad_request(
        "API endpoint not found.",
        404
    )


# application entry point

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
