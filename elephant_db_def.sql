CREATE TABLE elephants (
id INT(10) NOT NULL primary key auto_increment,
num INT(12) NOT NULL UNIQUE,
name VARCHAR(128),
sex ENUM('F','M','UKN') NOT NULL DEFAULT 'UKN',
birth DATE NOT NULL,
cw ENUM('captive','wild','UKN') NOT NULL DEFAULT 'UKN',
age_capture INT(2),
camp VARCHAR(64),
alive ENUM('Y','N','UKN') NOT NULL DEFAULT 'UKN',
commits TEXT
);

CREATE TABLE health (
id INT(12) NOT NULL primary key auto_increment,
elephant_id INT(10) NOT NULL,
date DATE NOT NULL,
loc VARCHAR(64),
type ENUM('accident','disease','death') NOT NULL,
code INT(4) NOT NULL,
commits TEXT
);

CREATE TABLE health_code (
id INT(4) NOT NULL primary key auto_increment,
code VARCHAR(12) NOT NULL UNIQUE,
descript TEXT,
commits TEXT
);

CREATE TABLE breeding (
id INT(12) NOT NULL primary key auto_increment,
elephant_id INT(10) NOT NULL,
date DATE NOT NULL,
loc VARCHAR(64) NOT NULL,
offspring_id INT(10), #Needs to refer to elephants.id but can be null if offspring unknown / dead before id
offspring_alive ENUM('Y','N','U'), #Need to look at data -> needed here if offspring not in table 'elephants'. So data here should be something like survived to age X
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
elephant_id INT(10) NOT NULL,
date DATE,
measure INT(4) NOT NULL,
value FLOAT NOT NULL,
commits TEXT
);

CREATE TABLE measures_code (
id INT(4) NOT NULL primary key auto_increment,
code VARCHAR(12) NOT NULL UNIQUE,
unit VARCHAR(12) NOT NULL,
descript TEXT,
commits TEXT
);

CREATE TABLE commits (
id INT(10) NOT NULL primary key auto_increment,
stamp VARCHAR(14) NOT NULL UNIQUE, #format YYYYMMDDHHMMSS
user VARCHAR(12) NOT NULL,
details TEXT,
commits TEXT
);

ALTER TABLE `elephants` ENGINE = InnoDB ;
ALTER TABLE `health` ENGINE = InnoDB ;
ALTER TABLE `health_code` ENGINE = InnoDB ;
ALTER TABLE `breeding` ENGINE = InnoDB ;
ALTER TABLE `pedigree` ENGINE = InnoDB ;
ALTER TABLE `measures` ENGINE = InnoDB ;
ALTER TABLE `measures_code` ENGINE = InnoDB ;

ALTER TABLE `health` ADD INDEX (`elephant_id`);
ALTER TABLE `breeding` ADD INDEX (`elephant_id`);
ALTER TABLE `pedigree` ADD INDEX (`elephant_1_id`);
ALTER TABLE `pedigree` ADD INDEX (`elephant_2_id`);
ALTER TABLE `measures` ADD INDEX (`elephant_id`);

ALTER TABLE `health` ADD FOREIGN KEY (`elephant_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `breeding` ADD FOREIGN KEY (`elephant_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `pedigree` ADD FOREIGN KEY (`elephant_1_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `pedigree` ADD FOREIGN KEY (`elephant_2_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE `measures` ADD FOREIGN KEY (`elephant_id`) REFERENCES `elephants` (`id`) ON DELETE CASCADE ON UPDATE CASCADE ;

