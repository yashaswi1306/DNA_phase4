# Schema Changes and Errors Fixed (`schema.sql`)

**Baseline:** Team 37's Phase 3 relational schema (the final Stage D design, 29 relations), which converted Team 46's Phase 2 EER for our Mini World (World Beard and Moustache Championships, Team 50's Phase 1 document).

**Teams to cite in the README:** Phase 2 = Team 46, Phase 3 = Team 37.

**Tested on:** MySQL 8.0. The final `schema.sql` runs with zero errors, creates all 29 tables, and can be re-run on an existing database (the `DROP DATABASE` at the top handles that).

---

## 1. Errors fixed

| # | Error | Why it failed / mattered | Fix |
|---|-------|--------------------------|-----|
| 1 | The comment `--SUBCLASSES` had no space after `--` | MySQL needs a space after `--`. Otherwise the script stops with `ERROR 1064` at that line and every table after it (COMPETITOR onwards) is never created | Changed to `-- SUBCLASSES` |
| 2 | The Phase 3 attribute `Group` (in `OFFERS` and `GROUP_COVERAGE`) is a reserved word in MySQL | `CREATE TABLE` fails if it is used unquoted | Renamed to `Category_Group` in both tables, including the composite FK `(Champ_ID, Category_Group)` |
| 3 | The Phase 3 attribute `Rank` (in `HOST_BID`) is a reserved word in MySQL 8 | Same problem | Kept the name but wrapped it in backticks (`` `Rank` ``) everywhere it appears, including its CHECK |
| 4 | Foreign keys with `ON UPDATE CASCADE` on columns that also appear in a CHECK constraint | MySQL rejects this with `ERROR 3823` | Used `ON UPDATE RESTRICT` on exactly three foreign keys: `OFFICER_APPOINTMENT.Club_ID` (CHECK on Club_ID), `TICKET (Champ_ID, Valid_On)` (CHECK on Valid_On) and `CHANGE_RECORD.Approved_By` (CHECK on Approved_By). Every other FK uses `ON UPDATE CASCADE` |
| 5 | Table creation order | A child table created before its parent makes the FK fail | Tables are created parents first: independent entities, then CHAMPIONSHIP, multivalued tables, subclasses, then dependent tables (GROUP_COVERAGE before OFFERS, OFFERS and COMPETITOR_AT_EDITION before COMPETES_IN, COMPETES_IN before ENTRY_FOR_CLUB and CHANGE_RECORD) |

---

## 2. Design changes (for the README "Design Changes" section)

No entities or tables were added or removed. All 29 Phase 3 relations are kept, with the same primary keys and foreign keys.

| # | Change | Reason |
|---|--------|--------|
| 1 | Renamed `Group` to `Category_Group` in `OFFERS` and `GROUP_COVERAGE` | `GROUP` is a reserved SQL word |
| 2 | `OFFERS.Category_Group` is `NOT NULL` | Every offered category belongs to a group, and this makes the FK to `GROUP_COVERAGE` always enforced. Phase 3 said the FK applies "when Group is populated" (nullable). **Consequence:** a `GROUP_COVERAGE` row must exist before any `OFFERS` row that uses it |
| 3 | `PERSON.Display_Name` and `OFFERS.Display_Name` are `NOT NULL` | Display name is the name shown on the site, so every person and offer needs one (Given and Family names stay optional, since a nickname alone is allowed) |
| 4 | `TICKET.Holder_ID` is `NOT NULL` | A ticket is always held by someone |
| 5 | Added `UNIQUE` on `CHAMPIONSHIP.Year` and `CHAMPIONSHIP.Replaces_Champ_ID` | Year is the alternate key, and one edition can be replaced by at most one other (Phase 3 FD list) |
| 6 | Added `UNIQUE (Champ_ID, Competitor_No)` on `COMPETES_IN` | A competitor number is unique within an edition, and may be NULL for old results |
| 7 | Added CHECK: `CHAMPIONSHIP` registration close date is not before the open date, `Max_Categories_Per_Competitor > 0`, `Year >= 1990` | Basic validity rules |
| 8 | Added CHECK on `TICKET`: a `Day` ticket must have `Valid_On`, a `Weekend` ticket must not. Also `Price >= 0`, `Ticket_No > 0` | Implements the Phase 2 change C2 (`Valid_On`) |
| 9 | Added CHECK on `OFFICER_APPOINTMENT`: `Host_Club_Vice_President` must have a `Club_ID`, `Term_End_Year >= Term_Start_Year`, `Term_Start_Year >= 2004` | Phase 3 kept the Position-to-Club rule as a CHECK instead of an FD |
| 10 | Added CHECK on `OFFERS`: lengths and ages are non-negative and min is not above max | Valid category rules |
| 11 | Added CHECK on `COMPETES_IN`: `Checked_In` is TRUE exactly when `Check_In_At` is set. Also score, placement and beard length are non-negative, placement is at least 1, and competitor number is positive | Keeps check-in data consistent (Phase 3 said to use a CHECK rather than treat these as FDs) |
| 12 | Added CHECK on `CHANGE_RECORD`: a Pending request has no `Decided_At`, Approved or Rejected requests do, and an Approved request must have `Approved_By` | Matches the "nullable while pending" rule |
| 13 | Added CHECK on `HOST_BID` (`Bid_No > 0`, `Votes >= 0`, `Rank > 0`) and on `CHAMP_ATTENDANCE_CLAIM` (`Reported_Count >= 0`) | Valid counts |
| 14 | Chose data types and ENUMs: `INT`/`VARCHAR`/`TEXT`/`DATE`/`DATETIME`/`DECIMAL`/`CHAR(3)` plus ENUMs for Membership_Status, Championship Status, Position, Ticket Type/Access/Status, Bid Status/Eligibility, Results_Coverage, Styling_Aids, Rules_Verified, Entry_Status, Role and Change Status | Phase 3 gave no data types |
| 15 | Referential actions: `ON DELETE RESTRICT` on every FK, `ON UPDATE CASCADE` on all except the three in error 4 above | The data is historical results, so deleting a parent that still has children is blocked instead of silently removing history |
| 16 | Added indexes: Championship (Status, Year), Person (Display_Name), Club (Name), Category (Name), Host_Bid (Status), Competes_In (Champ_ID + Placement, and Champ_ID + Category_ID + Score), Offers (Champ_ID + Category_Group), Ticket (Champ_ID + Status) | Columns used in search, filter and ranking queries |

---

## 3. Please confirm with the team

- **`Year >= 1990` and `Term_Start_Year >= 2004`** are our assumptions about the earliest data. If the website lists an older championship or officer term, loosen these CHECKs or `populate.sql` will fail.
- **`OFFERS.Category_Group NOT NULL`** is stricter than Phase 3. If any category on the website has no group, make it nullable.
- **`idx_championship_year`** is redundant, because `Year` is already `UNIQUE` and so already indexed. It can be removed.
- **`ON DELETE RESTRICT` everywhere** means the demo "delete" operation must target a row with no children (for example a ticket, a club alias, or an entry with no `ENTRY_FOR_CLUB` or `CHANGE_RECORD` rows), or the child rows must be deleted first.
