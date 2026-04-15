CREATE DATABASE LibraryDB;
USE LibraryDB;

-- Table 1: Books
CREATE TABLE Books (
    book_id INT PRIMARY KEY,
    title VARCHAR(100),
    category VARCHAR(50)
);

-- Table 2: Students
CREATE TABLE Students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    last_active DATE
);

-- Table 3: IssuedBooks
CREATE TABLE IssuedBooks (
    issue_id INT PRIMARY KEY,
    student_id INT,
    book_id INT,
    issue_date DATE,
    return_date DATE,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

-- Insert sample data
INSERT INTO Books VALUES
(1, 'Java Basics', 'Programming'),
(2, 'SQL Guide', 'Database'),
(3, 'History of India', 'History'),
(4, 'Python Intro', 'Programming');

INSERT INTO Students VALUES
(101, 'Ravi', '2024-01-10'),
(102, 'Sita', '2022-05-12'),
(103, 'Arjun', '2023-11-20');

INSERT INTO IssuedBooks VALUES
(1, 101, 1, '2026-03-01', NULL),
(2, 102, 2, '2026-03-20', '2026-03-25'),
(3, 103, 3, '2026-03-10', NULL);

-- 1. Overdue Books (More than 14 days, not returned)
SELECT s.name, b.title, i.issue_date
FROM IssuedBooks i
JOIN Students s ON i.student_id = s.student_id
JOIN Books b ON i.book_id = b.book_id
WHERE i.return_date IS NULL
AND DATEDIFF(CURDATE(), i.issue_date) > 14;

-- 2. Most Popular Category
SELECT category, COUNT(*) AS total_borrows
FROM Books b
JOIN IssuedBooks i ON b.book_id = i.book_id
GROUP BY category
ORDER BY total_borrows DESC;

SET SQL_SAFE_UPDATES=0;

-- 3. Remove Inactive Students (3+ years)
DELETE FROM IssuedBooks
WHERE student_id IN (
    SELECT student_id FROM (
        SELECT student_id 
        FROM Students
        WHERE DATEDIFF(CURDATE(), last_active) > 1095
    ) AS temp
);

DELETE FROM Students
WHERE DATEDIFF(CURDATE(), last_active) > 1095;