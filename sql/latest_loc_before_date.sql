DELIMITER //
CREATE FUNCTION LATEST_LOC_BEFORE(ele INT(4), ymd DATE)
RETURNS VARCHAR (32)
DETERMINISTIC
BEGIN
SET @LATEST_LOC=(SELECT location.code FROM (SELECT ALL_LOCS.id, ALL_LOCS.loc, ALL_LOCS.d AS date
	FROM (SELECT elephants.id, elephants.camp as loc, elephants.birth AS d FROM elephants WHERE elephants.id = ele AND elephants.camp is not null
    UNION ALL 
    SELECT events.elephant_id AS id, events.loc, events.date AS d FROM events WHERE events.elephant_id = ele AND events.loc is not null) AS ALL_LOCS
WHERE
    ALL_LOCS.loc IS NOT NULL AND d <= ymd ORDER BY d DESC LIMIT 1) AS LATEST
    INNER JOIN location on LATEST.loc = location.id);
RETURN @LATEST_LOC;
END//

