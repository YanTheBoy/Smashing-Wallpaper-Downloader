# Выборка с дублированием (одинаковые значения)
SELECT * FROM employee 
WHERE salary = (SELECT MAX(salary) FROM employee AS i WHERE i.department = employee.department);

# Выборка без дублирования
SELECT name,department,salary 
FROM( 
	SELECT( 
		SELECT id 
		FROM employee ti 
		WHERE ti.department=t1.department 
		ORDER BY ti.salary DESC LIMIT 
		1)lid 
	FROM( 
		SELECT DISTINCT department 
		FROM employee) t1 
	)ro, employee t2 
WHERE t2.id = ro.lid; 