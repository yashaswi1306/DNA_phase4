# DNA_phase4

## RElational Schema using Mysql

**DBMS:** MariaDB 10.11 | **Database:** `wbmc_db`


## Changes still needed
- Add backend/trigger validation for category limits, registration windows, age limits, minimum host-bid representatives, Best in Show eligibility, cancelled-edition results, approval of completed-result changes, rescheduling and self-replacement.
- Use transactions for multi-step operations and protect concurrent category-limit checks.
- Verify FK mappings and ENUM values against Stage D; test invalid inserts and confirm the test row is absent.
- Confirm the design choice: Phase 1's `ENTRY` alternative or Stage D's ternary `COMPETES_IN`.

## Important
- `src/schema_fixed.sql` starts with `DROP DATABASE IF EXISTS wbmc_db;`; rerunning it deletes the database and data. Back up is needed first.

##########################################

part 2: populate.sql

added parent tables, then weak and bridge tables, and so on. checked constraints. Tables populated.

Imp: 
In schema.sql, all foreign keys are defined with ON DELETE RESTRICT. RESTRICT prevents you from deleting a row in a parent table if any child table points to it.
If in the future we attempt to demonstrate the web application's DELETE feature by deleting a parent record (e.g., a person or championship that has children in COMPETES_IN or TICKET), MySQL will reject it with an unhandled foreign key error.
So, we have provided isolated, demo-ready leaf records (such as a pending ticket or a pending change record) that can be deleted cleanly during the video demo without breaking foreign key integrity. A leaf record is a row that references its parents, but no other table references it.

Testing later can be done on:


Query 1 (Search by Name/Text): Search competitors by Display_Name (e.g., 'Bryan', 'Langum', 'Aarne').

Query 2 (Filter by Status/Group): Filter championships by Status = 'Completed' vs 'Upcoming', or categories by Styling_Aids = 'Allowed'.

Query 3 (Join Detail View): Championship page joining CHAMPIONSHIP, VENUE, CLUB, and CHAMP_EVENT_DATE.

Query 4 (Leaderboard/Aggregation): Calculate average scores per category, or count competitor entries by country.

Query 5 (Multi-table Profile): Competitor profile displaying their registered club, event history, scores, and Best-in-Show awards.

Update 1 (CREATE/INSERT Demo): Form to book a spectator ticket or register a new competitor.

Update 2 (UPDATE Demo): Competitor check-in for Pittsburgh 2025:
Competitor Lucas Vance (Person_ID 16, Competitor_No 401) is seeded as Checked_In = FALSE, Check_In_At = NULL, Entry_Status = 'Registered'.
In the UI demo, clicking "Check In" updates this row to Checked_In=TRUE, Check_In_At=NOW() , Entry_Status='Checked_in'.

Update 3 (DELETE Demo):
Ticket (Champ_ID=4, Ticket_No=999) is an active spectator ticket with NO dependent records.
In the UI demo, cancelling/refunding this ticket executes a clean DELETE that succeeds immediately and can be verified in the SQL shell.


AI use: Had ai check my manual entries.

######################################
