/*
The pivotal table `elephants` is the center of the database. Holds all immutable information about each individual. `num`
is the MTE-attributed ID number, name is usual name (if several they are separated by comas). Calf num obeys to syntax
[BIRTH YEAR][A|B][MOTHER NUMBER] (B as standard for 'baby', A in case of a twin baby). `alive` should be changed to a
boolean  for `dead`.
*/

CREATE TABLE elephants (
id INT(10) NOT NULL primary key auto_increment,
num VARCHAR(10) UNIQUE,
name VARCHAR(128),
calf_num VARCHAR(10),
sex ENUM('F','M','UKN') NOT NULL DEFAULT 'UKN',
birth DATE NOT NULL,
cw ENUM('captive','wild','UKN') NOT NULL DEFAULT 'UKN',
age_capture INT(2),
camp INT(4),
alive ENUM('Y','N','UKN') NOT NULL DEFAULT 'UKN',
research ENUM('Y','N') NOT NULL DEFAULT 'N',
commits TEXT
);


/*
The `pedigree` table holds infoprimarmation about relationships between pairs of individuals. `unknown` will be used only with
a genetically-derived relationship coefficient (in that case the nature of the relationship is impossible to determine.
Each relationship is entered twice in symmetric ways (Relationship 1 = {A mother of B ~ B offspring of A}).
*/

CREATE TABLE pedigree (
id INT(12) NOT NULL primary key auto_increment,
rel_id INT(12) NOT NULL,
elephant_1_id INT(10) NOT NULL,
elephant_2_id INT(10) NOT NULL,
rel ENUM('mother','father','offspring','unknown') NOT NULL DEFAULT 'unknown',
coef FLOAT,
commits TEXT
);

/*
The `logbooks` table holds the content of the logbooks in a raw form, only translated and parsed to a minimum. No
attempt is made to regularise or understand the contents except in the ENUM fields (which mostly reflect codes already
enforced by the vets). The `elephant_id` field is foreign-keyed to the `elephants` table.
*/

CREATE TABLE logbooks (
id INT(12) NOT NULL PRIMARY KEY auto_increment,
elephant_id INT(10) NOT NULL,
date DATE NOT NULL,
health ENUM('FFF','FF','N'),
teeth ENUM('normal', 'medium', 'worn'),
chain ENUM('fair','medium','bad'),
breeding ENUM('suspected_pregnant', 'pregnant', 'not_pregnant', 'calving', 'miscarriage', 'lactating', 'full_mammary', 'musth'),
wounds TEXT,
disease TEXT,
seriousness ENUM('high','medium','low'),
work TEXT,
food TEXT,
treatment TEXT,
details TEXT,
commits TEXT
);

/*
The tables `events` and `event_code` describe all events that have a time and a place. Details of event types are in the
`event_code` table, although details about one particular instance of that event are in the `events` table. By nature,
events are analysed: they represent an expert decision/diagnosis about something that happened, as opposed to the raw
logbook data.
*/

CREATE TABLE events (
id INT(12) NOT NULL primary key auto_increment,
elephant_id INT(10) NOT NULL,
date DATE NOT NULL,
loc INT(4),
code INT(4) NOT NULL,
details TEXT,
commits TEXT
);

CREATE TABLE event_code (
id INT(4) NOT NULL primary key auto_increment,
class ENUM('capture','taming','accident','health','death','alive','metadata') NOT NULL,
type VARCHAR(24) NOT NULL UNIQUE,
descript TEXT,
commits TEXT
);

/*
Structured as the `events` table. Each data point is unique. The `measure_id` field refers to the row in the original
dataset, as a convenience to retrieve the batches of input data in case one problem needs to be audited.
*/

CREATE TABLE measures (
id INT(12) NOT NULL primary key auto_increment,
measure_id INT(12) NOT NULL,
elephant_id INT(10) NOT NULL,
date DATE,
code INT(4) NOT NULL,
value FLOAT NOT NULL,
experiment INT(4),
batch TEXT,
details TEXT,
commits TEXT
);

CREATE TABLE measure_code (id INT(4) NOT NULL primary key auto_increment,
class ENUM('morphology','physiology','behaviour','parasitology','immunology','genomics') NOT NULL,
type VARCHAR(12) NOT NULL UNIQUE,
unit VARCHAR(12) NOT NULL,
descript TEXT,
commits TEXT
);

CREATE TABLE experiments (
id INT(4) NOT NULL primary key auto_increment,
experiment VARCHAR(128) NOT NULL,
details TEXT NOT NULL,
commits TEXT
);

/*
The `location` table aims at interfacing with QGIS. Joint will be made on the code, which is unique and defined by the
Myanmar Information and Management Unit.
*/

CREATE TABLE location (
id INT(4) NOT NULL primary key auto_increment,
code VARCHAR(32) UNIQUE,
name VARCHAR(32),
level ENUM('agency','division','district','township','village')
);

/*
The `remarks`table is a free-form comment table. Ultimately it will be open to INSERT by all users. Made to store any
type of notes not fitting in any other template (a characteristic physical trait, an anecdote, etc...)
 */

CREATE TABLE remarks (
id INT(12) NOT NULL primary key auto_increment,
elephant_id INT(10) NOT NULL,
remark TEXT,
author VARCHAR(16)
);

/*
The `commits` tabe holds the track change system. Each commit corresponds to an input event, which is documented outside
the database by input files and error logs.
*/

CREATE TABLE commits (
id INT(10) NOT NULL primary key auto_increment,
stamp VARCHAR(14) NOT NULL UNIQUE, #format YYYYMMDDHHMMSS
user VARCHAR(12) NOT NULL,
details TEXT
);


ALTER TABLE `elephants` ENGINE = InnoDB ;
ALTER TABLE `remarks` ENGINE = InnoDB ;
ALTER TABLE `events` ENGINE = InnoDB ;
ALTER TABLE `event_code` ENGINE = InnoDB ;
ALTER TABLE `logbooks` ENGINE = InnoDB ;
ALTER TABLE `pedigree` ENGINE = InnoDB ;
ALTER TABLE `measures` ENGINE = InnoDB ;
ALTER TABLE `measure_code` ENGINE = InnoDB ;
ALTER TABLE `experiments` ENGINE = InnoDB ;
ALTER TABLE `location` ENGINE = InnoDB ;


ALTER TABLE elephants ADD INDEX (`id`);
ALTER TABLE `elephants` ADD INDEX (`camp`);
ALTER TABLE `remarks` ADD INDEX (`elephant_id`);
ALTER TABLE `events` ADD INDEX (`elephant_id`);
ALTER TABLE `events` ADD INDEX (`code`);
ALTER TABLE `events` ADD INDEX (`loc`);
ALTER TABLE `logbooks` ADD INDEX (`elephant_id`);
ALTER TABLE `pedigree` ADD INDEX (`elephant_1_id`);
ALTER TABLE `pedigree` ADD INDEX (`elephant_2_id`);
ALTER TABLE `measures` ADD INDEX (`elephant_id`);
ALTER TABLE `measures` ADD INDEX (`code`);
ALTER TABLE `measures` ADD INDEX (`experiment`);
ALTER TABLE `location` ADD INDEX (`id`);


ALTER TABLE `remarks` ADD FOREIGN KEY (`elephant_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `events` ADD FOREIGN KEY (`elephant_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `events` ADD FOREIGN KEY (`code`) REFERENCES `event_code` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `events` ADD FOREIGN KEY (`loc`) REFERENCES `location` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `logbooks` ADD FOREIGN KEY (`elephant_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `pedigree` ADD FOREIGN KEY (`elephant_1_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `pedigree` ADD FOREIGN KEY (`elephant_2_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `measures` ADD FOREIGN KEY (`elephant_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `measures` ADD FOREIGN KEY (`code`) REFERENCES `measure_code` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `measures` ADD FOREIGN KEY (`experiment`) REFERENCES `experiments` (`id`) ON UPDATE CASCADE ;
ALTER TABLE `elephants` ADD FOREIGN KEY (`camp`) REFERENCES `location` (`id`) ON UPDATE CASCADE ;