# DNA Phase 4 — World Beard and Moustache Championships

## 1. Project Overview

This project implements a relational database and web application
for the World Beard and Moustache Championships (WBMC).

The application allows users to explore championship information,
search for competitors, view competition results, inspect competitor
profiles, create spectator tickets, check in competitors and delete
tickets.

The project uses:

- **DBMS:** MariaDB 10.11
- **Database:** `wbmc_db`
- **Backend:** Python Flask
- **Database driver:** PyMySQL
- **Query language:** SQL
- **Frontend:** HTML, CSS and JavaScript (or another frontend framework)

The backend communicates with MariaDB through PyMySQL.
The frontend communicates with the backend through HTTP/JSON APIs.

No ORM, ODM, OGM or query builder is used.

---

## 2. Repository Structure

```text
DNA_phase4/
│
├── README.md
├── BACKEND_API.md
│
└── src/
    ├── schema.sql
    ├── populate.sql
    ├── app.py
    ├── config.py
    ├── db.py
    └── requirements.txt
```

### File descriptions

| File | Description |
|---|---|
| `schema.sql` | Creates the relational database schema |
| `populate.sql` | Inserts the project data |
| `app.py` | Flask application and HTTP routes |
| `config.py` | Database and application configuration |
| `db.py` | Database connection and raw SQL functions |
| `requirements.txt` | Python dependencies |
| `BACKEND_API.md` | API endpoint documentation |

---

## 3. Database Setup

### Requirements

Install the following:

- Python 3
- MariaDB 10.11
- MariaDB command-line client
- pip

### Create and populate the database

From the repository root, run:

```bash
mysql -u root -p < src/schema.sql
```

Then:

```bash
mysql -u root -p < src/populate.sql
```

The schema script creates `wbmc_db` and its tables.
The population script inserts the championship, competitor,
category, ticket and other project data.

**WARNING:** The schema script drops and recreates the database.
Running it again will destroy existing database contents.
Do not rerun it after making changes or performing the demo
unless you intend to reset the database.

---

## 4. Backend Setup

### Create a virtual environment

From the repository root:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r src/requirements.txt
```

### Configure database credentials

The backend reads its configuration from environment variables.

```bash
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DB_USER=root
export DB_PASS="your_password"
export DB_NAME=wbmc_db
```

An optional Flask secret key can be configured using:

```bash
export FLASK_SECRET_KEY="your-secret-key"
```

If environment variables are not provided, the application
uses the defaults defined in `config.py`.

### Start the application

From the repository root:

```bash
python src/app.py
```

The backend will run at:

```text
http://127.0.0.1:5000
```

The root endpoint provides an API overview:

```text
http://127.0.0.1:5000/
```

Health check:

```text
http://127.0.0.1:5000/health
```

---

## 5. Backend Architecture

The backend is divided into three modules.

### config.py

Responsible for:

- Reading database credentials from environment variables.
- Providing connection configuration.
- Defining the Flask secret key.

### db.py

Responsible for:

- Establishing and closing database connections.
- Executing parameterised SQL queries.
- Performing joins, filtering and aggregation inside MariaDB.
- Managing transactions for write operations.
- Validating database-related input.
- Handling missing records.

### app.py

Responsible for:

- Defining Flask routes.
- Reading query parameters and JSON request bodies.
- Validating HTTP request input.
- Calling functions from `db.py`.
- Returning JSON responses.
- Handling errors.

### Request flow

```text
User Interface
      |
      | HTTP Request
      v
   Flask (app.py)
      |
      | Validation
      v
Database Layer (db.py)
      |
      | Parameterised SQL
      v
   MariaDB
      |
      | Query Results
      v
Database Layer (db.py)
      |
      v
   Flask (app.py)
      |
      | JSON Response
      v
User Interface
```

The browser never connects directly to MariaDB.

---

## 6. Functional Requirements

The application implements five read operations and three
write operations.

### 6.1 Read Operations

#### 1. Search Competitors

Search competitors by their display name.

- Tables: `PERSON`, `COMPETITOR`
- Search uses partial matching.
- Results are ordered alphabetically.

Example:

```text
GET /api/competitors?q=Bryan
```

#### 2. Filter Championships

Filter championships by status and category styling-aid rules.

- Tables: `CHAMPIONSHIP`, `OFFERS`
- Supports championship status filtering.
- Supports styling-aid filtering.

Example:

```text
GET /api/championships?status=Completed
```

Another example:

```text
GET /api/championships?styling_aids=Allowed
```

Supported championship statuses:

- `Upcoming`
- `In_progress`
- `Completed`
- `Cancelled`

Supported styling-aid values:

- `None`
- `Moustache_only`
- `Allowed`

#### 3. Championship Details

Retrieve detailed information about a championship.

- Tables: `CHAMPIONSHIP`, `VENUE`, `CLUB`,
  `CHAMP_EVENT_DATE`
- Includes host location, venue, host club,
  registration dates and event dates.

Example:

```text
GET /api/championships/4
```

#### 4. Leaderboard

Retrieve competitor results for a championship.

- Tables: `COMPETES_IN`, `PERSON`, `CATEGORY`
- Includes competitor names, scores, placements
  and beard lengths.
- Optionally filters by category.

Example:

```text
GET /api/leaderboard?champ_id=4
```

With category filtering:

```text
GET /api/leaderboard?champ_id=4&category_id=14
```

#### 5. Competitor Profile

Retrieve a competitor's profile and participation history.

- Tables: `PERSON`, `COMPETITOR`, `MEMBER_OF`,
  `CLUB`, `COMPETES_IN`, `CHAMPIONSHIP`,
  `CATEGORY`, `BEST_IN_SHOW`
- Includes personal information, club memberships,
  championship participation and awards.

Example:

```text
GET /api/competitors/16
```

---

### 6.2 Write Operations

#### 6. Create Ticket

Create a new ticket for a championship.

- Table: `TICKET`
- Checks that the championship and ticket holder exist.
- Validates ticket type, access type, price and currency.
- Validates the event date for Day tickets.
- Allocates the next ticket number.
- Uses a transaction.

Endpoint:

```text
POST /api/tickets
```

Example JSON body:

```json
{
    "champ_id": 4,
    "holder_id": 17,
    "type": "Spectator",
    "access": "Weekend",
    "price": 50.00,
    "currency": "USD"
}
```

For a Day ticket, provide `valid_on`:

```json
{
    "champ_id": 4,
    "holder_id": 17,
    "type": "Spectator",
    "access": "Day",
    "price": 30.00,
    "currency": "USD",
    "valid_on": "2025-07-05"
}
```

#### 7. Competitor Check-in

Check in a registered competitor.

- Table: `COMPETES_IN`
- Updates `Checked_In` to TRUE.
- Sets `Check_In_At` to the current timestamp.
- Changes `Entry_Status` to `Checked_in`.
- Only permits entries that are currently registered
  and have not already been checked in.

Endpoint:

```text
POST /api/competitions/check-in
```

Example JSON body:

```json
{
    "person_id": 16,
    "category_id": 14,
    "champ_id": 4
}
```

#### 8. Delete Ticket

Delete an existing ticket.

- Table: `TICKET`
- Identifies tickets using their composite primary key.
- Uses a transaction.
- Returns an error if the ticket does not exist
  or a database constraint prevents deletion.

Endpoint:

```text
DELETE /api/tickets/4/999
```

---

## 7. Demo-Ready Database Records

The population script includes specific records for demonstrating
the three write operations.

### Create: New spectator ticket

Use an existing person and championship.

For example:

```json
{
    "champ_id": 4,
    "holder_id": 17,
    "type": "Spectator",
    "access": "Weekend",
    "price": 50.00,
    "currency": "USD"
}
```

The backend generates a ticket number and inserts
the new ticket.

### Update: Competitor check-in

The population script contains a registered competitor
for Pittsburgh 2025:

| Attribute | Value |
|---|---|
| Competitor | Lucas Vance |
| Person_ID | 16 |
| Competitor_No | 401 |
| Category_ID | 14 |
| Champ_ID | 4 |
| Checked_In | FALSE |
| Check_In_At | NULL |
| Entry_Status | Registered |

The check-in operation changes:

```text
Checked_In  = TRUE
Check_In_At = CURRENT_TIMESTAMP
Entry_Status = 'Checked_in'
```

### Delete: Demo ticket

The population script contains a ticket specifically
intended for the DELETE demonstration.

| Attribute | Value |
|---|---|
| Champ_ID | 4 |
| Ticket_No | 999 |
| Type | Spectator |
| Access | Day |
| Price | 30.00 USD |
| Status | Valid |
| Holder_ID | 17 |

The ticket has no dependent records and can be
deleted without violating the existing foreign keys.

Endpoint:

```text
DELETE /api/tickets/4/999
```

---

## 8. API Response Format

Successful responses use the following format:

```json
{
    "ok": true,
    "data": []
}
```

An error response looks like:

```json
{
    "ok": false,
    "error": "Competitor not found."
}
```

HTTP status codes:

| Status | Meaning |
|---|---|
| 200 | Successful read/update/delete |
| 201 | Successfully created |
| 400 | Invalid request or input |
| 404 | Requested resource not found |
| 409 | Operation conflicts with current state or constraints |
| 500 | Internal database error |

Dates and timestamps are converted to ISO-formatted
strings before being returned as JSON.

Decimal database values are converted to JSON numbers.

---

## 9. Query Safety and Transactions

### Parameterised Queries

All SQL queries use PyMySQL parameter placeholders.

Example:

```python
sql = """
    SELECT *
    FROM PERSON
    WHERE Person_ID = %s
"""

cur.execute(sql, (person_id,))
```

User input is never directly concatenated into SQL strings.

### Transactions

Write operations use explicit transaction handling.

Successful operations are committed:

```python
conn.commit()
```

Failed operations are rolled back:

```python
conn.rollback()
```

### Database Constraints

The application relies on MariaDB for primary-key,
foreign-key, ENUM and CHECK constraint enforcement.

Foreign keys in the existing schema use `ON DELETE RESTRICT`.
Therefore, deleting a parent record with dependent rows
is rejected by the database.

---

## 10. Known Limitations and Further Validation

The current backend implements the eight required operations
and their basic input and database error handling.

The following domain-specific business rules still require
additional implementation and testing:

- Category participation limits.
- Championship registration windows.
- Competitor age limits for categories.
- Minimum host-bid representatives.
- Best in Show eligibility.
- Handling results for cancelled championships.
- Approval of changes to completed results.
- Championship rescheduling and self-replacement rules.

These rules must be implemented in the backend and/or
database triggers where required by the project design.

The ticket creation operation currently validates the
ticket fields, championship, holder and event date.
It does not implement every possible ticket-related
business rule.

The check-in operation verifies that the entry is registered
and not already checked in.

The backend should be tested against the actual populated
database before the final demonstration.

---

## 11. Testing

Start the backend:

```bash
python src/app.py
```

Test the health endpoint:

```bash
curl http://127.0.0.1:5000/health
```

Search competitors:

```bash
curl "http://127.0.0.1:5000/api/competitors?q=Bryan"
```

Filter championships:

```bash
curl "http://127.0.0.1:5000/api/championships?status=Completed"
```

Get championship details:

```bash
curl http://127.0.0.1:5000/api/championships/4
```

Get leaderboard:

```bash
curl "http://127.0.0.1:5000/api/leaderboard?champ_id=4&category_id=14"
```

Get competitor profile:

```bash
curl http://127.0.0.1:5000/api/competitors/16
```

Create a ticket:

```bash
curl -X POST http://127.0.0.1:5000/api/tickets \
-H "Content-Type: application/json" \
-d '{
    "champ_id": 4,
    "holder_id": 17,
    "type": "Spectator",
    "access": "Weekend",
    "price": 50,
    "currency": "USD"
}'
```

Check in Lucas Vance:

```bash
curl -X POST http://127.0.0.1:5000/api/competitions/check-in \
-H "Content-Type: application/json" \
-d '{
    "person_id": 16,
    "category_id": 14,
    "champ_id": 4
}'
```

Delete the demo ticket:

```bash
curl -X DELETE \
http://127.0.0.1:5000/api/tickets/4/999
```

Verify database changes using the MariaDB client.

---

## 12. Frontend Integration

The frontend must communicate with the Flask backend
using HTTP requests.

Examples:

```javascript
// Search competitors
const response = await fetch(
    "/api/competitors?q=Bryan"
);

const result = await response.json();
```

```javascript
// Check in a competitor
const response = await fetch(
    "/api/competitions/check-in",
    {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            person_id: 16,
            category_id: 14,
            champ_id: 4
        })
    }
);

const result = await response.json();
```

If the frontend runs on a different port,
configure a development proxy or enable CORS on Flask.

The frontend must never connect directly to MariaDB.

---

## 13. Submission and Demonstration

The final project demonstration should show:

1. The web application running in a browser.
2. The MariaDB client or GUI displaying the database.
3. Each of the five read operations.
4. The CREATE operation before and after insertion.
5. The UPDATE operation before and after check-in.
6. The DELETE operation before and after deletion.

For every write operation, demonstrate the corresponding
database change using the same query before and after
the operation.

The frontend feature list in the README should match
the order of the demonstration video.

---

## 14. Team Responsibilities

| Person | Responsibility |
|---|---|
| P1 | Database schema, design review and design changes |
| P2 | Data extraction, population script and data quality |
| P3 | Python backend, SQL functions, routes and error handling |
| P4 | Frontend, templates, CSS, navigation and documentation |

The backend exposes JSON endpoints for P4 to integrate
with the web interface.
