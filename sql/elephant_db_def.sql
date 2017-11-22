CREATE TABLE elephants (
id INT(10) NOT NULL primary key auto_increment,
num VARCHAR(10) UNIQUE,
name VARCHAR(128),
calf_num VARCHAR(10),
sex ENUM('F','M','UKN') NOT NULL DEFAULT 'UKN',
birth DATE NOT NULL,
cw ENUM('captive','wild','UKN') NOT NULL DEFAULT 'UKN',
age_capture INT(2),
camp VARCHAR(64),
alive ENUM('Y','N','UKN') NOT NULL DEFAULT 'UKN',
research ENUM('Y','N') NOT NULL DEFAULT 'N',
commits TEXT
);

CREATE TABLE remarks (
id INT(12) NOT NULL primary key auto_increment,
elephant_id INT(10) NOT NULL,
remark TEXT
);

CREATE TABLE events (
id INT(12) NOT NULL primary key auto_increment,
elephant_id INT(10) NOT NULL,
date DATE NOT NULL,
loc VARCHAR(64),
code INT(4) NOT NULL,
commits TEXT
);

CREATE TABLE event_code (
id INT(4) NOT NULL primary key auto_increment,
class ENUM('capture','accident','health','death','alive','metadata') NOT NULL,
type VARCHAR(12) NOT NULL UNIQUE,
descript TEXT,
commits TEXT
);

CREATE TABLE pedigree (
id INT(12) NOT NULL primary key auto_increment,
rel_id INT(12) NOT NULL,
elephant_1_id INT(10) NOT NULL,
elephant_2_id INT(10) NOT NULL,
rel ENUM('mother','father','offspring','unknown') NOT NULL DEFAULT 'unknown',
coef FLOAT,
commits TEXT
);

CREATE TABLE measures (
id INT(12) NOT NULL primary key auto_increment,
measure_id INT(12) NOT NULL,
elephant_id INT(10) NOT NULL,
date DATE,
code INT(4) NOT NULL,
value FLOAT NOT NULL,
commits TEXT
);

CREATE TABLE measure_code (
id INT(4) NOT NULL primary key auto_increment,
class ENUM('morphology','physiology','behaviour','parasitology','immunology','genomics') NOT NULL,
type VARCHAR(12) NOT NULL UNIQUE,
unit VARCHAR(12) NOT NULL,
descript TEXT,
commits TEXT
);

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
ALTER TABLE `pedigree` ENGINE = InnoDB ;
ALTER TABLE `measures` ENGINE = InnoDB ;
ALTER TABLE `measure_code` ENGINE = InnoDB ;

ALTER TABLE `events` ADD INDEX (`elephant_id`);
ALTER TABLE `remarks` ADD INDEX (`elephant_id`);
ALTER TABLE `events` ADD INDEX (`code`);
ALTER TABLE `pedigree` ADD INDEX (`elephant_1_id`);
ALTER TABLE `pedigree` ADD INDEX (`elephant_2_id`);
ALTER TABLE `measures` ADD INDEX (`elephant_id`);
ALTER TABLE `measures` ADD INDEX (`measure`);

ALTER TABLE `remarks` ADD FOREIGN KEY (`elephant_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `events` ADD FOREIGN KEY (`elephant_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `events` ADD FOREIGN KEY (`code`) REFERENCES `event_code` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `pedigree` ADD FOREIGN KEY (`elephant_1_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `pedigree` ADD FOREIGN KEY (`elephant_2_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `measures` ADD FOREIGN KEY (`elephant_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `measures` ADD FOREIGN KEY (`measure`) REFERENCES `measure_code` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
