USE company;

SELECT * FROM employee;

-- Search by Employee Name
SELECT *
FROM employee
WHERE ename LIKE '%Nikita%';

-- Search by Email
SELECT *
FROM employee
WHERE email LIKE '%gmail%';

-- Search by City
SELECT *
FROM employee
WHERE city LIKE '%Pune%';

-- Pagination
SELECT *
FROM employee
LIMIT 5 OFFSET 0;

SELECT *
FROM employee
LIMIT 5 OFFSET 5;

SELECT *
FROM employee
LIMIT 5 OFFSET 10;

-- Sort by Employee Name
SELECT *
FROM employee
ORDER BY ename ASC;

SELECT *
FROM employee
ORDER BY ename DESC;

ALTER TABLE employee
ADD COLUMN email VARCHAR(100),
ADD COLUMN city VARCHAR(100);
UPDATE employee
SET email='john@gmail.com', city='Pune'
WHERE id=1;

UPDATE employee
SET email='siya@gmail.com', city='Mumbai'
WHERE id=2;

UPDATE employee
SET email='ram@gmail.com', city='Satara'
WHERE id=3;

UPDATE employee
SET email='riya@gmail.com', city='Kolhapur'
WHERE id=4;

UPDATE employee
SET email='shyam@gmail.com', city='Nashik'
WHERE id=5;

UPDATE employee
SET email='priya@gmail.com', city='Pune'
WHERE id=7;

UPDATE employee
SET email='rohan@gmail.com', city='Nagpur'
WHERE id=8;

UPDATE employee
SET email='neha@gmail.com', city='Aurangabad'
WHERE id=9;

UPDATE employee
SET email='samu@gmail.com', city='Sangli'
WHERE id=10;

UPDATE employee
SET email='raghav@gmail.com', city='Solapur'
WHERE id=11;