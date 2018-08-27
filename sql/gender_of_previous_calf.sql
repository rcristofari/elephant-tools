DELIMITER //
CREATE FUNCTION ELDER_SIB_GENDER(Calf INT(12))
RETURNS ENUM('M','F','UKN')
DETERMINISTIC
BEGIN
SET @rownum := 0;
SET @This_order = (SELECT BirthOrder FROM
		(SELECT @rownum := @rownum + 1 AS BirthOrder, MotherNum, MotherBirth, CalfID, CalfNum, CalfBirth FROM
			(SELECT e2.num AS MotherNum, e1.birth AS MotherBirth, e2.id AS CalfID, e2.num AS CalfNum, e2.birth AS CalfBirth FROM pedigree
			INNER JOIN elephants AS e1 ON pedigree.elephant_1_id = e1.id
			INNER JOIN elephants AS e2 ON pedigree.elephant_2_id = e2.id
			WHERE pedigree.elephant_1_id = (SELECT e1.id AS MotherID FROM pedigree
       			INNER JOIN elephants AS e1 ON pedigree.elephant_1_id = e1.id
				INNER JOIN elephants AS e2 ON pedigree.elephant_2_id = e2.id
				WHERE pedigree.rel = 'mother' AND elephant_2_id = Calf)
			AND pedigree.rel =  'mother'
			ORDER BY CalfBirth ASC) AS ordered) AS ranking
            WHERE CalfID = Calf);

SET @rownum := 0;
SET @SibGender = (SELECT SibGender FROM
		(SELECT @rownum := @rownum + 1 AS rank, SibGender FROM
			(SELECT e2.num AS MotherNum, e1.birth AS MotherBirth, e2.id AS CalfID, e2.sex AS SibGender, e2.birth AS CalfBirth FROM pedigree
			INNER JOIN elephants AS e1 ON pedigree.elephant_1_id = e1.id
			INNER JOIN elephants AS e2 ON pedigree.elephant_2_id = e2.id
			WHERE pedigree.elephant_1_id = (SELECT e1.id AS MotherID FROM pedigree
       			INNER JOIN elephants AS e1 ON pedigree.elephant_1_id = e1.id
				INNER JOIN elephants AS e2 ON pedigree.elephant_2_id = e2.id
				WHERE pedigree.rel = 'mother' AND elephant_2_id = Calf)
			AND pedigree.rel =  'mother'
			ORDER BY CalfBirth ASC) AS ordered) AS ranking
            WHERE rank = (@This_order - 1));
RETURN @SibGender;
END//