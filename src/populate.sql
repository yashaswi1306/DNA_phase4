USE wbmc_db;

-- independent parent tables

INSERT INTO PERSON (Person_ID, Given_Name, Family_Name, Nickname, Display_Name, Date_of_Birth, Hometown_City, Hometown_Region, Hometown_Country) VALUES
(1, 'Norbert', 'Topf', 'The President', 'Norbert Topf', '1958-04-12', 'Leogang', 'Salzburg', 'Austria'),
(2, 'Bryan', 'Nelson', 'B-Rex', 'Bryan Nelson', '1981-09-24', 'Austin', 'Texas', 'USA'),
(3, 'Jørgen', 'Bech-Pedersen', 'The Dane', 'Jørgen Bech-Pedersen', '1962-11-03', 'Copenhagen', 'Hovedstaden', 'Denmark'),
(4, 'Jeff', 'Langum', 'Big Red', 'Jeff Langum', '1976-03-15', 'Philadelphia', 'Pennsylvania', 'USA'),
(5, 'MJ', 'Johnson', 'Razor Free', 'MJ Johnson', '1984-07-29', 'Minneapolis', 'Minnesota', 'USA'),
(6, 'Aarne', 'Bielefeldt', 'The Wizard', 'Aarne Bielefeldt', '1965-06-18', 'Willits', 'California', 'USA'),
(7, 'Patrick', 'Fette', 'The Aristocrat', 'Patrick Fette', '1979-12-05', 'Louisville', 'Kentucky', 'USA'),
(8, 'Jason', 'Kiley', 'The Sculptor', 'Jason Kiley', '1983-02-14', 'Oneonta', 'New York', 'USA'),
(9, 'Michael', 'Wollin', 'Der Bartmeister', 'Michael Wollin', '1968-08-30', 'Höfen', 'Bavaria', 'Germany'),
(10, 'Jackie', 'Ellison', 'Texas Jack', 'Jackie Lynn Ellison', '1975-01-22', 'Houston', 'Texas', 'USA'),
(11, 'Wolfgang', 'Schneider', 'Kaiser', 'Wolfgang Schneider', '1955-10-10', 'Offenbach', 'Hesse', 'Germany'),
(12, 'Dan', 'Lawlor', 'Iron City Beard', 'Dan Lawlor', '1986-05-19', 'Pittsburgh', 'Pennsylvania', 'USA'),
(13, 'Patrick', 'Dawson', 'Gentleman Pat', 'Patrick Dawson', '1978-03-08', 'London', 'Greater London', 'United Kingdom'),
(14, 'Elena', 'Rostova', 'Whiskerina Queen', 'Elena Rostova', '1990-07-11', 'Austin', 'Texas', 'USA'),
(15, 'Sarah', 'Davies', 'Craft Maker', 'Sarah Davies', '1992-11-25', 'London', 'Greater London', 'United Kingdom'),
(16, 'Lucas', 'Vance', 'Iron Beard', 'Lucas Vance', '1991-04-18', 'Columbus', 'Ohio', 'USA'),
(17, 'Oliver', 'Queen', 'The Archer', 'Oliver Queen', '1988-06-20', 'Star City', 'Washington', 'USA'),
(18, 'Samir', 'Patel', 'The Windy Whiskers', 'Samir Patel', '1989-09-09', 'Chicago', 'Illinois', 'USA');

INSERT INTO CLUB (Club_ID, Name, Country, Membership_Status, Membership_As_Of) VALUES
(1, 'The Austin Facial Hair Club', 'USA', 'Member', '2015-01-01'),
(2, 'Snorrenclub Antwerpen', 'Belgium', 'Member', '2010-05-12'),
(3, 'Ostbayerischer Bart- und Schnurrbartverein', 'Germany', 'Member', '2012-08-20'),
(4, 'Three Rivers Beard & Moustache Club', 'USA', 'Member', '2020-03-15'),
(5, 'The British Beard Club', 'United Kingdom', 'Member', '2008-02-14'),
(6, 'Beard Team USA', 'USA', 'Member', '2005-06-01'),
(7, 'Club der Bartträger Höfen', 'Germany', 'Member', '2003-01-01'),
(8, 'World Whiskerinas Association', 'USA', 'Not_member', '2018-09-01');

INSERT INTO VENUE (Venue_ID, Name, Street, City, Region, Postal_Code, Country) VALUES
(1, 'The Long Center for the Performing Arts', '701 W Riverside Dr', 'Austin', 'Texas', '78704', 'USA'),
(2, 'Elisabeth Center Antwerp', 'Koningin Astridplein 26', 'Antwerp', 'Antwerp', '2018', 'Belgium'),
(3, 'Stadtsaal Burghausen', 'Kapuzinergasse 235', 'Burghausen', 'Bavaria', '84489', 'Germany'),
(4, 'David L. Lawrence Convention Center', '1000 Ft. Duquesne Blvd', 'Pittsburgh', 'Pennsylvania', '15222', 'USA'),
(5, 'Auckland Town Hall', 'Queen Street', 'Auckland', 'Auckland', '1010', 'New Zealand');

INSERT INTO CATEGORY (Category_ID, Name) VALUES
(1, 'Natural Moustache'),
(2, 'English Moustache'),
(3, 'Dali Moustache'),
(4, 'Imperial Moustache'),
(5, 'Hungarian Moustache'),
(6, 'Freestyle Moustache'),
(7, 'Natural Goatee'),
(8, 'Musketeer'),
(9, 'Fu Manchu'),
(10, 'Imperial Partial Beard'),
(11, 'Freestyle Partial Beard'),
(12, 'Verdi'),
(13, 'Garibaldi'),
(14, 'Full Beard Natural'),
(15, 'Full Beard with Styled Moustache'),
(16, 'Full Beard Freestyle'),
(17, 'Craft Beard Realistic'),
(18, 'Craft Beard Creative');

INSERT INTO CHARITY (Charity_ID, Name, Website) VALUES
(1, 'Livestrong Foundation', 'https://www.livestrong.org'),
(2, 'Burghausen Children Foundation', 'https://www.burghausen-kinderhilfe.de'),
(3, 'Greater Pittsburgh Community Food Bank', 'https://www.pittsburghfoodbank.org'),
(4, 'Antwerp Youth Care Fund', 'https://www.jeugdzorgantwerpen.be');

-- multi valued attributes for independent entities

INSERT INTO PERSON_ALIAS (Person_ID, Alias) VALUES
(4, 'The Philadelphian Beard'),
(5, 'The Stache Master'),
(6, 'The Redwood Sculptor'),
(8, 'The Beard Aristocrat');

INSERT INTO PERSON_EMAIL (Person_ID, Email) VALUES
(1, 'president@worldbeardchampionships.com'),
(2, 'bryan@austinfacialhairclub.com'),
(3, 'jorgen@danishbeard.dk'),
(4, 'jeff.langum@gmail.com'),
(5, 'mj.johnson@freestyle-stache.com'),
(6, 'aarne.bielefeldt@mendocino.com'),
(7, 'patrick.fette@whiskermail.com'),
(8, 'jason.kiley@gmail.com'),
(9, 'michael.wollin@bartclub-hoefen.de'),
(10, 'jackie.ellison@texasbeards.org'),
(12, 'dan@threeriversbeard.com'),
(16, 'lucas.vance@testmail.com'),
(17, 'oliver.queen@testmail.com'),
(18, 'samir.patel@testmail.com');

INSERT INTO CLUB_ALIAS (Club_ID, Alias) VALUES
(1, 'AFHC'),
(2, 'SNA'),
(3, 'OBSV Burghausen'),
(4, '3B'),
(5, 'BBC UK'),
(6, 'BTUSA');

INSERT INTO CLUB_WEB_LINK (Club_ID, Web_Link) VALUES
(1, 'https://austinfacialhairclub.com'),
(2, 'https://snorrenclub.be'),
(3, 'https://bartclub-burghausen.de'),
(4, 'https://threeriversbeard.com'),
(5, 'https://thebritishbeardclub.org'),
(6, 'https://beardteamusa.org');

INSERT INTO CATEGORY_ALIAS (Category_ID, Alias) VALUES
(6, 'Freestyle Stache'),
(12, 'Full Beard Verdi'),
(13, 'Full Beard Garibaldi'),
(14, 'Natural Full Beard'),
(16, 'Open Freestyle Beard');