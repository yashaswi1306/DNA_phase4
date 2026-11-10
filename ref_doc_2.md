# Phase 4 Implementation Plan

I haven't seen your Mini World, so this plan is generic. Swap in your actual entities and website where needed.

## Step 0: Decisions to make together (Day 1)

1. **Pick the paradigm.** I'd recommend **MySQL**. Phase 3 was relational, so you skip the *Schema Mapping* section, keep the schema nearly unchanged, and the boilerplate (PyMySQL + Flask) maps directly onto it.
2. **Pick the stack.** Flask with Jinja templates is the simplest option. The frontend lives in the same project and there's no CORS or separate build.
3. **Choose which of the two other teams' Phase 3 designs to use.** Note their team numbers, since the README needs them.
4. **Review that schema as a group.** List errors, missing tables, and lost Phase 1 requirements. Every change goes into a shared "Design Changes" doc with a one-line reason.
5. **Define the features up front.** Write down at least 5 queries and 3 updates (at least 1 create, 1 update, 1 delete), and the page and UI element that triggers each. Example:

| # | Feature | Type | Where in UI |
|---|---|---|---|
| 1 | Search items by name | Read | Search bar `/search?q=` |
| 2 | Filter by category/date | Read | Filter dropdown |
| 3 | Detail page with joined data | Read | `/item/<id>` |
| 4 | Aggregation (top-rated, counts) | Read | Home or stats page |
| 5 | Another join or filter query | Read | Any page |
| 6 | Add a record | Create | Form |
| 7 | Edit a record | Update | Edit form |
| 8 | Delete a record | Delete | Delete button |

6. **Set up a GitHub repo** with this structure:
```
src/
  schema.sql
  populate.sql
  app.py
  config.py
  db.py            (connection + query functions)
  requirements.txt
  templates/
  static/
README.md
```

## Step 1: Database implementation

- Translate the Phase 3 schema into `CREATE TABLE` statements.
- Start with `DROP DATABASE IF EXISTS`, then `CREATE DATABASE` and `USE`.
- Choose proper data types (`VARCHAR`, `DECIMAL(10,2)`, `DATE`, `ENUM`).
- Add PKs, FKs with `ON DELETE` and `ON UPDATE` actions that match your world's rules, plus `NOT NULL`, `UNIQUE` and `CHECK`.
- Add indexes on columns used in `WHERE`, `ORDER BY` and `JOIN`.
- Test by running `mysql -u user -p < schema.sql` on a fresh server.

## Step 2: Data population

- Extract real data from the website, using GenAI or scraping to help. No `test1` or `test2` placeholders.
- Insert parent tables before child tables.
- Include data that matches and doesn't match each query, and rows that are safe to update or delete in the demo. Without this, your queries can't be demonstrated meaningfully.
- Test by running `schema.sql` then `populate.sql` on a fresh server, and make sure it works end to end every time.

## Step 3: Backend

- Write `config.py` or use environment variables for DB credentials.
- Write `get_connection()` as in the boilerplate.
- Write one data-access function per feature, using **raw SQL with `%s` parameters** (never f-strings). No ORMs, and do joins and aggregation in SQL, not Python.
- Wrap writes in try/commit/rollback/finally.
- Write Flask routes that call these functions, and handle errors with `flash()` for constraint violations or missing records.

## Step 4: Frontend

- Build Jinja templates with a base layout and navigation, modelled on the real website's pages and flow.
- Display results as tables, cards or lists. Show friendly messages for "no results" and for errors.
- Add the forms and buttons that trigger every query and update. A free-text box for raw SQL does not count.

## Step 5: Integration and testing

- Run the full flow on a clean machine: schema, then populate, then `pip install -r requirements.txt`, then `python app.py`.
- Test every feature, including bad input, FK violations, and deleting a row that has dependents.
- Run `pip freeze` or hand-write `requirements.txt`.

## Step 6: Documentation, video and packaging

- Finish the README (contents listed below).
- Record the video of up to 10 minutes.
- Zip everything as `<team_number>.zip`.

## Dividing the work among 4 people

| Person | Role | Owns |
|---|---|---|
| **P1** | Database lead | `schema.sql`, review of the other team's design, revisions, and the Design Changes section |
| **P2** | Data lead | `populate.sql`, data extraction (GenAI or scraping), data quality, and demo-ready rows for updates and deletes |
| **P3** | Backend lead | `app.py`, `config.py`, `db.py`, all 8 raw-SQL functions, routes, and error handling |
| **P4** | Frontend and docs lead | Templates, CSS and navigation, the README, and the final packaging |

To keep the load balanced, split the queries and updates between P3 and P1. For example, P3 writes the 5 read queries and P1 writes the 3 write operations, since P1 knows the schema best and finishes early. P2 helps test the queries against the data, and P4 builds the pages as P3 finishes each route. Whoever writes the SQL for a feature should also write its README entry.

**Everyone together** reviews the Phase 3 design in Step 0, does integration testing in Step 5, and joins the video. A good split is P4 on the browser window and P1 or P2 on the SQL shell, with P3 narrating.

## Suggested timeline

| Phase | Who | What |
|---|---|---|
| Days 1-2 | All | Step 0 decisions and design review |
| Days 2-5 | P1 → P2 | Schema first, then population (P2 can draft data while P1 finalises the schema) |
| Days 3-8 | P3 + P4 | Backend and frontend in parallel, using agreed function names |
| Days 8-10 | All | Integration, testing and bug fixes |
| Days 10-12 | P4 + all | README, video and zip |

## What the README must contain

1. Paradigm, DBMS and versions
2. Backend framework and frontend stack
3. **Design Changes** (the two team numbers, plus every change with a one-line reason)
4. Setup and run instructions (load schema and population, install dependencies, start the app, URL)
5. Numbered feature list, in the same order as your video demo
6. A Schema Mapping section is only needed if you pick MongoDB or Neo4j

## Video checklist (10 minutes max)

- **Opening (30-60 seconds):** show the main pages and name the website you modelled.
- **For each update:** run a query in the DB shell to show the data before, perform the operation in the UI, then re-run the exact same query to show the change.
- **For each query:** run it from the web interface and show the correct result.
- **Layout:** two windows, the web app and the DB shell.

## Pitfalls to avoid

- Building SQL with f-strings. Always use `%s` parameters.
- Using SQLAlchemy, Django ORM or `pandas.to_sql`.
- Fetching whole tables and filtering in Python.
- A schema or populate script that fails on a fresh server.
- A README feature list that doesn't match the video order.
- A zip with the wrong name, or files not at the root level.

If you tell me your Mini World (the website and its main tables), I can help you define the specific 5 queries and 3 updates, sketch the pages, or write the starter `app.py` and `schema.sql`. Which paradigm are you leaning towards?
