/* This view summarises basic life history parameter for each elephant */
CREATE VIEW `eleview` AS
    (SELECT
        elephants.id AS id,
        elephants.num AS num,
        elephants.name AS name,
        elephants.calf_num AS calf_num,
        elephants.sex AS sex,
        elephants.birth AS birth,
        elephants.cw AS cw,
        elephants.age_capture AS age_capture,
        DATE_ADD(elephants.birth,
            INTERVAL elephants.age_capture YEAR) AS date_capture,
        location.name AS agency,
        location.code AS geo,
        elephants.research AS research,
        IFNULL(lrsJ.lrs, 0) AS lrs,
        elephants.alive AS alive,
        evJ.date AS death,
        evJ.type AS cause,
        Censoring.LastAliveDate AS last_alive,
        Censoring.Reason AS reason,
        IF(evJ.date IS NULL, ROUND(DATEDIFF(Censoring.LastAliveDate, elephants.birth) / 365.25, 2), ROUND(DATEDIFF(evJ.date, elephants.birth) / 365.25, 2)) AS lifespan,
        IFNULL(ROUND(DATEDIFF(evJ.date, elephants.birth) / 365.25,
                        2),
                ROUND(DATEDIFF(NOW(), elephants.birth) / 365.25,
                        2)) AS current_age,
        Censoring.Censored AS censored
    FROM
        elephants
            INNER JOIN
        (SELECT
            elephant_id,
                BirthDate,
                LastOffspringDate,
                LastEventDate,
                LastMeasureDate,
                LastAliveDate,
                DeathDate,
                Censored,
                CASE
                    WHEN LastAliveDate = LastOffspringDate THEN 'Breeding'
                    WHEN LastAliveDate = LastEventDate THEN 'Event'
                    WHEN LastAliveDate = LastMeasureDate THEN 'Measure'
                    WHEN LastAliveDate = BirthDate THEN 'Birth'
                    ELSE 'Unknown'
                END AS Reason
        FROM
            (SELECT
            elephant_id,
                BirthDeath.BirthDate,
                LastOffspringDate,
                LastEventDate,
                LastMeasureDate,
                IF(LastAlive.LastAliveDate > 0, LastAlive.LastAliveDate, BirthDeath.BirthDate) AS LastAliveDate,
                BirthDeath.DeathDate,
                IF(BirthDeath.DeathDate IS NULL, 0, 1) AS Censored
        FROM
            (SELECT
            elephants.id AS elephant_id,
                COALESCE(LastOffspring.date, 0) AS LastOffspringDate,
                COALESCE(LastEvent.date, 0) AS LastEventDate,
                COALESCE(LastMeasure.date, 0) AS LastMeasureDate,
                GREATEST(COALESCE(LastOffspring.date, 0), COALESCE(LastEvent.date, 0), COALESCE(LastMeasure.date, 0)) AS LastAliveDate
        FROM
            elephants
        LEFT JOIN (SELECT
            p.elephant_2_id, MAX(e1.birth) AS date
        FROM
            pedigree AS p
        INNER JOIN elephants AS e1 ON p.elephant_1_id = e1.id
        WHERE
            p.rel = 'offspring'
        GROUP BY elephant_2_id) AS LastOffspring ON elephants.id = LastOffspring.elephant_2_id
        LEFT JOIN (SELECT
            elephant_id, MAX(date) AS date
        FROM
            evview
        WHERE
            class != 'death'
        GROUP BY elephant_id) AS LastEvent ON elephants.id = LastEvent.elephant_id
        LEFT JOIN (SELECT
            elephant_id, MAX(date) AS date
        FROM
            msview
        GROUP BY elephant_id) AS LastMeasure ON elephants.id = LastMeasure.elephant_id
        GROUP BY elephants.id) AS LastAlive
        LEFT JOIN (SELECT
            elephants.id AS id,
                elephants.birth AS BirthDate,
                events.date AS DeathDate
        FROM
            elephants
        LEFT JOIN events ON elephants.id = events.elephant_id
        INNER JOIN event_code ON events.code = event_code.id
        WHERE
            event_code.class = 'death') AS BirthDeath ON LastAlive.elephant_id = BirthDeath.id) AS Dates) AS Censoring ON elephants.id = Censoring.elephant_id
            LEFT JOIN
        (SELECT
            elephants.id AS id,
                events.date AS date,
                event_code.class AS class,
                event_code.type AS type
        FROM
            elephants
        LEFT JOIN events ON elephants.id = events.elephant_id
        INNER JOIN event_code ON events.code = event_code.id
        WHERE
            event_code.class = 'death') AS evJ ON evJ.id = elephants.id
            LEFT JOIN
        location ON elephants.camp = location.id
            LEFT JOIN
        (SELECT
            elephants.id AS id, COUNT(pedigree.id) AS lrs
        FROM
            pedigree
        INNER JOIN elephants ON pedigree.elephant_2_id = elephants.id
        WHERE
            rel = 'offspring'
        GROUP BY elephants.id) AS lrsJ ON lrsJ.id = elephants.id);

/*
CREATE VIEW `eleview` AS
    SELECT
        elephants.id AS id,
        elephants.num AS num,
        elephants.name AS name,
        elephants.calf_num AS calf_num,
        elephants.sex AS sex,
        elephants.birth AS birth,
        elephants.cw AS cw,
        elephants.age_capture AS age_capture,
        DATE_ADD(elephants.birth,
            INTERVAL elephants.age_capture YEAR) AS date_capture,
        location.name AS agency,
        location.code AS geo,
        elephants.alive AS alive,
        elephants.research AS research,
        IFNULL(lrsJ.lrs, 0) AS lrs,
        evJ.date AS death,
        evJ.type AS cause,
        IFNULL(ROUND(DATEDIFF(evJ.date, elephants.birth) / 365.25,
                        1),
                ROUND(DATEDIFF(NOW(), elephants.birth) / 365.25,
                        1)) AS lifespan,
        IF(DATEDIFF(evJ.date, elephants.birth),
            1,
            0) AS censored
    FROM
        (SELECT
            elephants.id AS id,
                events.date AS date,
                event_code.class AS class,
                event_code.type AS type
        FROM
            elephants
        LEFT JOIN events ON elephants.id = events.elephant_id
        INNER JOIN event_code ON events.code = event_code.id
        WHERE
            event_code.class = 'death') AS evJ
            RIGHT JOIN
        elephants ON evJ.id = elephants.id
            LEFT JOIN
        location ON elephants.camp = location.id
            LEFT JOIN
        (SELECT
            elephants.id AS id, COUNT(pedigree.id) AS lrs
        FROM
            pedigree
        INNER JOIN elephants ON pedigree.elephant_2_id = elephants.id
        WHERE
            rel = 'offspring'
        GROUP BY elephants.id) AS lrsJ ON lrsJ.id = elephants.id
;
*/


/* These views gather name and number of the parents */

CREATE VIEW `mothers` AS
    SELECT
        e2.id AS id, e2.num as num, e2.calf_num as calf_num, e2.name as name, e1.num AS mother_num, e1.name AS mother_name
    FROM
        pedigree
            LEFT JOIN
        elephants AS e1 ON pedigree.elephant_1_id = e1.id
            LEFT JOIN
        elephants AS e2 ON pedigree.elephant_2_id = e2.id
    WHERE
        pedigree.rel = 'mother'
    ORDER BY e2.num;


CREATE VIEW `fathers` AS
    SELECT
        e2.id AS id, e2.num as num, e2.calf_num as calf_num, e2.name as name, e1.num AS father_num, e1.name AS father_name
    FROM
        pedigree
            LEFT JOIN
        elephants AS e1 ON pedigree.elephant_1_id = e1.id
            LEFT JOIN
        elephants AS e2 ON pedigree.elephant_2_id = e2.id
    WHERE
        pedigree.rel = 'father'
    ORDER BY e2.num;

/* This view summarises the measure points */
CREATE VIEW `msview` AS
    SELECT
        measures.id AS id,
        measures.measure_id AS measure_id,
        elephants.id AS elephant_id,
        elephants.num AS num,
        elephants.calf_num AS calf_num,
        elephants.name AS name,
        elephants.sex AS sex,
        measures.date AS date,
        measure_code.class AS class,
        measure_code.type AS type,
        measures.value AS value,
        measure_code.unit AS unit,
        measure_code.descript AS descript
    FROM
        measures
            INNER JOIN
        measure_code ON measures.code = measure_code.id
            INNER JOIN
        elephants ON measures.elephant_id = elephants.id
    ORDER BY elephants.num
;

/* Only the latest measure for each available measure type */

CREATE VIEW `latest_measures` AS
    SELECT
        id,
        measure_id,
        elephant_id,
        num,
        calf_num,
        name,
        sex,
        MAX(date) AS date,
        class,
        type,
        value,
        unit,
        descript
    FROM
        msview
    GROUP BY elephant_id, type;

/* Latest morphological measures for all relevant elephants */

CREATE VIEW `latest_morpho` AS
    SELECT
        m0.elephant_id,
        m0.num,
        m0.calf_num,
        m0.name,
        m0.sex,
        m1.value AS height,
        m2.value AS body_mass,
        m3.value AS neck,
        m4.value AS chest,
        m5.value AS belly,
        m6.value AS hind_limb,
        m7.value AS foot,
        m8.value AS bcs,
        m9.value AS tuskness
    FROM
        (SELECT DISTINCT
            elephant_id, num, calf_num, name, sex
        FROM
            latest_measures) AS m0
            LEFT JOIN
        latest_measures AS m1 ON m1.elephant_id = m0.elephant_id
            AND m1.type = 'height'
            LEFT JOIN
        latest_measures AS m2 ON m2.elephant_id = m0.elephant_id
            AND m2.type = 'body_mass'
            LEFT JOIN
        latest_measures AS m3 ON m3.elephant_id = m0.elephant_id
            AND m3.type = 'neck'
            LEFT JOIN
        latest_measures AS m4 ON m4.elephant_id = m0.elephant_id
            AND m4.type = 'chest'
            LEFT JOIN
        latest_measures AS m5 ON m5.elephant_id = m0.elephant_id
            AND m5.type = 'belly'
            LEFT JOIN
        latest_measures AS m6 ON m6.elephant_id = m0.elephant_id
            AND m6.type = 'hind_limb'
            LEFT JOIN
        latest_measures AS m7 ON m7.elephant_id = m0.elephant_id
            AND m7.type = 'foot'
            LEFT JOIN
        latest_measures AS m8 ON m8.elephant_id = m0.elephant_id
            AND m8.type = 'bcs'
            LEFT JOIN
        latest_measures AS m9 ON m9.elephant_id = m0.elephant_id
            AND m9.type = 'tuskness'
    WHERE
        m1.value IS NOT NULL
            OR m2.value IS NOT NULL
            OR m3.value IS NOT NULL
            OR m4.value IS NOT NULL
            OR m5.value IS NOT NULL
            OR m6.value IS NOT NULL
            OR m7.value IS NOT NULL
            OR m8.value IS NOT NULL
    GROUP BY elephant_id
;

/* This view summarises events */
CREATE VIEW `evview` AS
    SELECT
        events.id AS id,
        elephants.id AS elephant_id,
        elephants.num AS num,
        elephants.calf_num AS calf_num,
        elephants.name AS name,
        elephants.sex AS sex,
        events.date AS date,
        location.name AS agency,
        location.code AS geo,
        event_code.class AS class,
        event_code.type AS type,
        events.details AS details,
        event_code.descript AS descript
    FROM
        events
            INNER JOIN
        event_code ON events.code = event_code.id
            INNER JOIN
        elephants ON events.elephant_id = elephants.id
            LEFT JOIN
        location ON events.loc = location.id
    ORDER BY elephants.num
;

/*
/* This view gathers censoring information */
CREATE VIEW `censoring` AS
    (SELECT
        elephant_id,
        BirthDate,
        LastAliveDate,
        Reason,
        DeathDate,
        Age,
        Censored
    FROM
        (SELECT
            elephant_id,
                BirthDate,
                LastOffspringDate,
                LastEventDate,
                LastMeasureDate,
                LastAliveDate,
                DeathDate,
                IF(DeathDate IS NULL, ROUND(DATEDIFF(LastAliveDate, BirthDate) / 365.25, 2), ROUND(DATEDIFF(DeathDate, BirthDate) / 365.25, 2)) AS Age,
                Censored,
                CASE
                    WHEN LastAliveDate = LastOffspringDate THEN 'Breeding'
                    WHEN LastAliveDate = LastEventDate THEN 'Event'
                    WHEN LastAliveDate = LastMeasureDate THEN 'Measure'
                    WHEN LastAliveDate = BirthDate THEN 'Birth'
                    ELSE 'Unknown'
                END AS Reason
        FROM
            (SELECT
            elephant_id,
                BirthDeath.BirthDate,
                LastOffspringDate,
                LastEventDate,
                LastMeasureDate,
                IF(LastAlive.LastAliveDate > 0, LastAlive.LastAliveDate, BirthDeath.BirthDate) AS LastAliveDate,
                BirthDeath.DeathDate,
                IF(BirthDeath.DeathDate IS NULL, 0, 1) AS Censored
        FROM
            (SELECT
            elephants.id AS elephant_id,
                COALESCE(LastOffspring.date, 0) AS LastOffspringDate,
                COALESCE(LastEvent.date, 0) AS LastEventDate,
                COALESCE(LastMeasure.date, 0) AS LastMeasureDate,
                GREATEST(COALESCE(LastOffspring.date, 0), COALESCE(LastEvent.date, 0), COALESCE(LastMeasure.date, 0)) AS LastAliveDate
        FROM
            elephants
        LEFT JOIN (SELECT
            p.elephant_2_id, MAX(e1.birth) AS date
        FROM
            pedigree AS p
        INNER JOIN elephants AS e1 ON p.elephant_1_id = e1.id
        WHERE
            p.rel = 'offspring'
        GROUP BY elephant_2_id) AS LastOffspring ON elephants.id = LastOffspring.elephant_2_id
        LEFT JOIN (SELECT
            elephant_id, MAX(date) AS date
        FROM
            evview
        WHERE
            class != 'death'
        GROUP BY elephant_id) AS LastEvent ON elephants.id = LastEvent.elephant_id
        LEFT JOIN (SELECT
            elephant_id, MAX(date) AS date
        FROM
            msview
        GROUP BY elephant_id) AS LastMeasure ON elephants.id = LastMeasure.elephant_id
        GROUP BY elephants.id) AS LastAlive
        LEFT JOIN (SELECT
            id, birth AS BirthDate, death AS DeathDate
        FROM
            eleview) AS BirthDeath ON LastAlive.elephant_id = BirthDeath.id) AS Dates) AS Censoring
            INNER JOIN
        elephants ON Censoring.elephant_id = elephants.id);
*/

/* A view gathering latest location information */

/*
THIS WAS WRONG:
CREATE VIEW `latest_loc` AS
    (SELECT
        elephant_id,
        elephants.num AS num,
        elephants.calf_num AS calf_num,
        MAX(date) AS date,
        loc,
        code
    FROM
        (SELECT
            elephants.id AS elephant_id,
                elephants.birth AS date,
                CONCAT(location.name, ' ', location.level) AS loc,
                location.code AS code
        FROM
            elephants
        INNER JOIN location ON elephants.camp = location.id UNION ALL SELECT
            events.elephant_id,
                events.date AS date,
                CONCAT(location.name, ' ', location.level) AS birth_loc,
                location.code AS code
        FROM
            events
        INNER JOIN location ON events.loc = location.id
        WHERE
            loc IS NOT NULL) AS locs
            INNER JOIN
        elephants ON elephants.id = locs.elephant_id
    GROUP BY elephant_id); */

CREATE VIEW `latest_loc` AS
(SELECT e.id,
		e.num,
        e.calf_num,
        e.date,
        CONCAT(location.name, ' ', location.level) AS loc,
        e.code 
FROM (SELECT 
    elephants.id,
    elephants.num,
    elephants.calf_num,
	GET_LATEST_LOC_DATE(elephants.id) as date,
    GET_LATEST_LOC(elephants.id) as code
FROM
    elephants) AS e
    INNER JOIN
    location ON e.code = location.code);
