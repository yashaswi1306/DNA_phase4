# DNA Phase 4 — World Beard and Moustache Championships

## Link for submission video 

https://drive.google.com/file/d/1De25jY9NbK6kR_OKAxWKT7GxDFCikeJq/view?usp=sharing

## 1. Project Overview

A relational database and web application for the
World Beard and Moustache Championships (WBMC), modelled on
worldbeardchampionships.com.

- **DBMS:** MySQL 9.6
- **Database:** `wbmc_db`
- **Backend:** Python Flask, PyMySQL
- **Query language:** SQL (raw, parameterised; no ORM)
- **Frontend:** Jinja templates (HTML) and CSS

---

## 2. Repository Structure

```text
DNA_phase4/
├── README.md
└── src/
    ├── schema.sql        creates the database
    ├── populate.sql      inserts the data
    ├── app.py            Flask routes
    ├── db.py             database connection and SQL queries
    ├── config.py         database settings
    ├── requirements.txt
    ├── templates/        HTML pages
    └── static/style.css
```

---

## 3. Setup

Start MySQL and load the database (from the repository root):

```bash
brew services start mysql
mysql -u root < src/schema.sql
mysql -u root < src/populate.sql
```

If your `root` user has a password, add `-p`.
Running both scripts again resets the database.

Install dependencies and start the app:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
python src/app.py
```

Open `http://127.0.0.1:5001`

Database login defaults to user `root` with no password
(see `config.py`). To change it, set `DB_USER` and `DB_PASS`.

---

## 4. Features

Listed in the same order as the demonstration video.

### Read Operations

1. **Search Competitors** — Competitors page (`/search?q=patrick`).
   Finds competitors by name or alias.
2. **Filter Championships** — Results page (`/`), choose a status
   and/or styling aids rule and click Filter. Lists championships with
   host club and number of categories.
3. **Championship Details** — click a year (`/championship/9`).
   Venue, dates, host club, Best in Show and charities.
4. **Results by Category** — on the championship page choose a category
   and click Show (`/championship/9?category=30`). Placings, hometowns
   and scores.
5. **Competitor Profile** — click a competitor name (`/competitor/9`).
   Hometown, clubs, awards and every championship entered.

### Write Operations

6. **Create Ticket (INSERT)** — Tickets page (`/tickets`), fill in the
   form and click Create ticket. Only for upcoming championships;
   the next ticket number is assigned automatically.
7. **Check In Competitor (UPDATE)** — Check-in page (`/checkin`),
   click Check in next to a registered competitor. Sets `Checked_In`,
   `Check_In_At` and `Entry_Status` in `COMPETES_IN`.
8. **Delete Ticket (DELETE)** — Tickets page, choose 2025 Pittsburgh
   and click Delete next to a ticket.

### Demo records

| Operation | Record |
|---|---|
| Create | Any ticket for 2027 Blackpool (`Champ_ID` 10) |
| Update | Brian Eva (`Person_ID` 184, `Category_ID` 30, `Champ_ID` 10) |
| Delete | Ticket 2 of 2025 Pittsburgh (`Champ_ID` 9) |

Queries to run in MySQL before and after each write:

```sql
USE wbmc_db;

SELECT * FROM TICKET WHERE Champ_ID = 10;

SELECT Person_ID, Checked_In, Check_In_At, Entry_Status
FROM COMPETES_IN WHERE Person_ID = 184 AND Champ_ID = 10;

SELECT * FROM TICKET WHERE Champ_ID = 9;
```

---

## 5. Design Changes

Phase 2 was done by **Team 46** and Phase 3 by **Team 37**.
We used Team 37's schema (29 relations); no tables were added or removed.

| Change | Reason |
|---|---|
| `--SUBCLASSES` changed to `-- SUBCLASSES` | Caused a syntax error |
| `Group` renamed to `Category_Group` | Reserved word |
| `Rank` written as `` `Rank` `` | Reserved word |
| `ON UPDATE RESTRICT` on 3 FKs whose columns are in a CHECK | MySQL does not allow CASCADE there |
| Tables reordered, parents first | Foreign keys failed otherwise |
| `NOT NULL` on `Category_Group`, `Display_Name`, `Holder_ID` | These always need a value |
| `UNIQUE` on `Year`, `Replaces_Champ_ID`, `(Champ_ID, Competitor_No)` | Alternate keys from Phase 3 |
| CHECK constraints (Day ticket needs a date, price >= 0, check-in time only when checked in, etc.) | Enforce Phase 2/3 rules |
| Data types and ENUMs for every column | Phase 3 had none |
| `ON DELETE RESTRICT` on all FKs | Old results can't be deleted by accident |
| Indexes on searched columns; duplicate `Year` index removed | Speed |
| Database uses `utf8mb4` | Names like Jürgen and Müge |

---

## 6. Data Sources

Results pages and history page on worldbeardchampionships.com
(2017, 2019 and 2025 top 3 per category) and news articles
(2027 Blackpool, ticket prices). Ticket numbers and holders and the
2027 registrations used for the check-in demo were added by us.

---

## 7. Team Responsibilities

| Person | Responsibility |
|---|---|
| P1 | Database schema, design review and design changes |
| P2 | Data extraction, population script and data quality |
| P3 | Python backend, SQL functions, routes and error handling |
| P4 | Frontend, templates, CSS, navigation and documentation |