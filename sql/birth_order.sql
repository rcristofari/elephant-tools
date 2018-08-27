DELIMITER //
CREATE FUNCTION BIRTH_ORDER(Calf INT(12))
RETURNS INT
DETERMINISTIC
BEGIN
SET @rownum := 0;
SET @BirthOrder = (SELECT BirthOrder FROM
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
RETURN @BirthOrder;
END//