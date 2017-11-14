SELECT a.num AS MotherNum, a.name AS Mother, a.birth AS MotherBirth, b.num AS OffspringNum, b.name AS Offspring, b.birth AS OffspringBirth FROM pedigree AS p LEFT JOIN elephants AS a ON p.elephant_1_id = a.id LEFT JOIN elephants AS b ON p.elephant_2_id = b.id WHERE p.rel = 'mother' AND a.num=2222 ORDER BY b.birth DESC;

select a.num, a.name as Mother, a.sex, a.birth, b.num, b.name as Offspring, b.sex, b.birth, round(datediff(b.birth, a.birth)/365.25) as Mother_Age from pedigree left join elephants as a on pedigree.elephant_1_id = a.id left join elephants as b on pedigree.elephant_2_id = b.id where pedigree.rel = "mother" order by Mother_Age DESC;


#Get all the descendants of one mother
SELECT 	a.num AS MotherNum, 
	a.name AS Mother, 
	a.birth AS MotherBirth, 
	b.num AS OffspringNum, 
	b.name AS Offspring, 
	b.birth AS OffspringBirth 
	FROM pedigree AS p 
	LEFT JOIN elephants AS a ON p.elephant_1_id = a.id 
	LEFT JOIN elephants AS b ON p.elephant_2_id = b.id 
	WHERE p.rel = 'mother' AND a.num=2222 
	ORDER BY b.birth ASC;


*/ Last offspring

SELECT 	MAX(b.birth) 
	FROM pedigree AS p 
	LEFT JOIN elephants AS a ON p.elephant_1_id = a.id 
	LEFT JOIN elephants AS b ON p.elephant_2_id = b.id 
	WHERE (p.rel = 'mother' OR p.rel = 'father') AND a.num=2222;


*/How many offsprings per mother?

SELECT elephants.id, num, name, birth, COUNT(pedigree.id) as offsprings FROM pedigree
	INNER JOIN elephants ON elephants.id = pedigree.elephant_1_id
	GROUP BY elephants.id
	HAVING offsprings > 3
	ORDER BY offsprings;


SELECT measures.measure_id, measure_code.code, measures.date, measures.value, measure_code.unit
	FROM measures 
	INNER JOIN measure_code on measures.measure = measure_code.id
	INNER JOIN elephants on measures.elephant_id = elephants.id 
	WHERE elephants.num=5709 
	AND measure_code.code='tusk';
