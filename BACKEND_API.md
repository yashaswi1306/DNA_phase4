
# P3 Backend API Contract

Base URL:

```text
http://127.0.0.1:5000
```

Run from the repository root:

```bash
python src/app.py
```

## API Endpoints

| Feature | Method | Endpoint |
|---|---|---|
| Competitor search | GET | `/api/competitors?q=Bryan` |
| Championship filter | GET | `/api/championships` |
| Championship details | GET | `/api/championships/4` |
| Leaderboard | GET | `/api/leaderboard?champ_id=4` |
| Competitor profile | GET | `/api/competitors/16` |
| Create ticket | POST | `/api/tickets` |
| Competitor check-in | POST | `/api/competitions/check-in` |
| Delete ticket | DELETE | `/api/tickets/4/999` |

## 1. Competitor Search

```http
GET /api/competitors?q=Bryan
```

Query parameter:
- `q`: competitor display name or partial name.

## 2. Championship Filter

```http
GET /api/championships?status=Completed&styling_aids=Allowed
```

Optional query parameters:
- `status`
- `styling_aids`

## 3. Championship Details

```http
GET /api/championships/4
```

Returns championship, venue, host club and event dates.

## 4. Leaderboard

```http
GET /api/leaderboard?champ_id=4&category_id=14
```

Parameters:
- `champ_id`: required.
- `category_id`: optional.

## 5. Competitor Profile

```http
GET /api/competitors/16
```

Returns profile, club memberships, event history and awards.

## 6. Create Ticket

```http
POST /api/tickets
Content-Type: application/json
```

Request:

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

For Weekend access, omit `valid_on` or send null.

The backend generates the ticket number.

## 7. Competitor Check-in

```http
POST /api/competitions/check-in
Content-Type: application/json
```

Request:

```json
{
    "person_id": 16,
    "category_id": 14,
    "champ_id": 4
}
```

This updates Lucas Vance's Pittsburgh 2025 entry.

## 8. Delete Ticket

```http
DELETE /api/tickets/4/999
```

Deletes the designated demo ticket.

## Response Format

Success:

```json
{
    "ok": true,
    "data": {}
}
```

Error:

```json
{
    "ok": false,
    "error": "Error description"
}
```

## HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Successful operation |
| 201 | Resource created |
| 400 | Invalid input |
| 404 | Resource not found |
| 409 | Operation conflict |
| 500 | Database error |

## Database Configuration

```bash
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DB_USER=root
export DB_PASS='your-password'
export DB_NAME=wbmc_db
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r src/requirements.txt

python src/app.py
```

Load `schema.sql` followed by `populate.sql` before starting the backend.

WARNING: schema.sql drops and recreates the database.
Do not rerun it unless you intend to reset the database.
