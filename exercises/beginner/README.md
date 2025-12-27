# Beginner Exercises

Welcome to the beginner exercises! These hands-on exercises will help you practice fundamental database concepts and operations.

## Prerequisites

Before starting these exercises, you should have:
- Completed reading the [Fundamentals](../../01-fundamentals/README.md) section
- Basic knowledge of Python or JavaScript
- Installed PostgreSQL or MySQL locally
- Basic understanding of SQL

## Exercise 1: Setting Up Your First Database

### Objective
Learn to create a database and basic tables with proper data types and constraints.

### Tasks

1. **Create a database called `library_db`**

2. **Create the following tables:**

```sql
-- Authors table
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_year INTEGER CHECK (birth_year > 1800 AND birth_year < 2100),
    country VARCHAR(50)
);

-- Books table
CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author_id INTEGER REFERENCES authors(author_id),
    publication_year INTEGER CHECK (publication_year > 1400),
    isbn VARCHAR(13) UNIQUE,
    genre VARCHAR(50),
    pages INTEGER CHECK (pages > 0),
    available_copies INTEGER DEFAULT 0 CHECK (available_copies >= 0)
);

-- Members table
CREATE TABLE members (
    member_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    join_date DATE DEFAULT CURRENT_DATE,
    membership_status VARCHAR(20) DEFAULT 'active'
        CHECK (membership_status IN ('active', 'expired', 'suspended'))
);

-- Borrowings table
CREATE TABLE borrowings (
    borrowing_id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES books(book_id),
    member_id INTEGER REFERENCES members(member_id),
    borrow_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    CONSTRAINT valid_dates CHECK (due_date > borrow_date)
);
```

3. **Verify your tables were created:**
```sql
-- List all tables
\dt

-- Describe each table structure
\d authors
\d books
\d members
\d borrowings
```

### Expected Outcome
You should have four tables with proper relationships (foreign keys) and constraints.

---

## Exercise 2: Basic CRUD Operations

### Objective
Practice inserting, reading, updating, and deleting data.

### Tasks

**1. INSERT - Add sample data:**

```sql
-- Add authors
INSERT INTO authors (first_name, last_name, birth_year, country)
VALUES
    ('George', 'Orwell', 1903, 'United Kingdom'),
    ('J.K.', 'Rowling', 1965, 'United Kingdom'),
    ('Stephen', 'King', 1947, 'United States'),
    ('Agatha', 'Christie', 1890, 'United Kingdom');

-- Add books
INSERT INTO books (title, author_id, publication_year, isbn, genre, pages, available_copies)
VALUES
    ('1984', 1, 1949, '9780451524935', 'Dystopian', 328, 5),
    ('Animal Farm', 1, 1945, '9780451526342', 'Political Fiction', 112, 3),
    ('Harry Potter and the Philosopher''s Stone', 2, 1997, '9780439708180', 'Fantasy', 309, 7),
    ('The Shining', 3, 1977, '9780385121675', 'Horror', 447, 4),
    ('Murder on the Orient Express', 4, 1934, '9780062693662', 'Mystery', 256, 2);

-- Add members
INSERT INTO members (first_name, last_name, email)
VALUES
    ('John', 'Doe', 'john.doe@email.com'),
    ('Jane', 'Smith', 'jane.smith@email.com'),
    ('Bob', 'Johnson', 'bob.johnson@email.com');
```

**2. SELECT - Query the data:**

```sql
-- a) List all authors
SELECT * FROM authors;

-- b) List all books with their authors
SELECT b.title, a.first_name, a.last_name, b.publication_year
FROM books b
JOIN authors a ON b.author_id = a.author_id;

-- c) Find books published after 1950
SELECT title, publication_year FROM books
WHERE publication_year > 1950
ORDER BY publication_year;

-- d) Count books by genre
SELECT genre, COUNT(*) as book_count
FROM books
GROUP BY genre
ORDER BY book_count DESC;
```

**3. UPDATE - Modify existing data:**

```sql
-- a) Update available copies when a book is borrowed
UPDATE books
SET available_copies = available_copies - 1
WHERE book_id = 1 AND available_copies > 0;

-- b) Update a member's email
UPDATE members
SET email = 'newemail@email.com'
WHERE member_id = 1;

-- c) Mark a member as inactive
UPDATE members
SET membership_status = 'expired'
WHERE member_id = 3;
```

**4. DELETE - Remove data:**

```sql
-- Delete a specific book (be careful with foreign keys!)
DELETE FROM books WHERE book_id = 5;

-- Delete expired memberships
DELETE FROM members WHERE membership_status = 'expired';
```

### Expected Outcome
You should be comfortable with basic SQL CRUD operations and understand how foreign keys affect deletions.

---

## Exercise 3: Queries with Filtering and Sorting

### Objective
Master WHERE clauses, operators, and sorting.

### Tasks

Write SQL queries to answer these questions:

**1. Basic Filtering:**
```sql
-- a) Find all books in the 'Fantasy' genre
SELECT * FROM books WHERE genre = 'Fantasy';

-- b) Find all authors born after 1900
SELECT * FROM authors WHERE birth_year > 1900;

-- c) Find members who joined in the last 30 days
SELECT * FROM members
WHERE join_date >= CURRENT_DATE - INTERVAL '30 days';
```

**2. Multiple Conditions:**
```sql
-- a) Find Fantasy books with more than 300 pages
SELECT * FROM books
WHERE genre = 'Fantasy' AND pages > 300;

-- b) Find books published between 1940 and 1980
SELECT * FROM books
WHERE publication_year BETWEEN 1940 AND 1980;

-- c) Find authors from UK or US
SELECT * FROM authors
WHERE country IN ('United Kingdom', 'United States');
```

**3. Pattern Matching:**
```sql
-- a) Find books with 'Harry' in the title
SELECT * FROM books WHERE title LIKE '%Harry%';

-- b) Find authors whose last name starts with 'K'
SELECT * FROM authors WHERE last_name LIKE 'K%';

-- c) Find members with gmail addresses
SELECT * FROM members WHERE email LIKE '%@gmail.com';
```

**4. Sorting:**
```sql
-- a) List books ordered by pages (longest first)
SELECT title, pages FROM books
ORDER BY pages DESC;

-- b) List authors alphabetically by last name
SELECT first_name, last_name FROM authors
ORDER BY last_name, first_name;

-- c) List books by publication year (newest first) and title
SELECT title, publication_year FROM books
ORDER BY publication_year DESC, title;
```

### Expected Outcome
You should understand various filtering techniques and sorting options in SQL.

---

## Exercise 4: Working with Relationships (JOINs)

### Objective
Learn to combine data from multiple tables using JOINs.

### Tasks

**1. INNER JOIN:**
```sql
-- a) List all books with their author names
SELECT
    b.title,
    a.first_name || ' ' || a.last_name AS author_name,
    b.publication_year
FROM books b
INNER JOIN authors a ON b.author_id = a.author_id;

-- b) List all borrowings with book and member details
SELECT
    m.first_name || ' ' || m.last_name AS member_name,
    b.title AS book_title,
    br.borrow_date,
    br.due_date
FROM borrowings br
INNER JOIN books b ON br.book_id = b.book_id
INNER JOIN members m ON br.member_id = m.member_id;
```

**2. LEFT JOIN:**
```sql
-- a) List all authors and their books (including authors without books)
SELECT
    a.first_name || ' ' || a.last_name AS author_name,
    b.title
FROM authors a
LEFT JOIN books b ON a.author_id = b.author_id
ORDER BY a.last_name;

-- b) List all members and their current borrowings (including members with no borrowings)
SELECT
    m.first_name || ' ' || m.last_name AS member_name,
    b.title AS borrowed_book
FROM members m
LEFT JOIN borrowings br ON m.member_id = br.member_id AND br.return_date IS NULL
LEFT JOIN books b ON br.book_id = b.book_id;
```

**3. Aggregations with JOINs:**
```sql
-- a) Count books per author
SELECT
    a.first_name || ' ' || a.last_name AS author_name,
    COUNT(b.book_id) AS book_count
FROM authors a
LEFT JOIN books b ON a.author_id = b.author_id
GROUP BY a.author_id, a.first_name, a.last_name
ORDER BY book_count DESC;

-- b) Find the most borrowed books
SELECT
    b.title,
    COUNT(br.borrowing_id) AS borrow_count
FROM books b
LEFT JOIN borrowings br ON b.book_id = br.book_id
GROUP BY b.book_id, b.title
ORDER BY borrow_count DESC
LIMIT 5;
```

### Expected Outcome
You should understand how to combine data from multiple tables and when to use different types of JOINs.

---

## Exercise 5: Python Integration

### Objective
Connect to the database from Python and perform operations programmatically.

### Tasks

Create a Python script `library_manager.py`:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
conn = psycopg2.connect(
    dbname="library_db",
    user="postgres",
    password="your_password",
    host="localhost"
)

def add_author(first_name, last_name, birth_year, country):
    """Add a new author to the database"""
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO authors (first_name, last_name, birth_year, country)
            VALUES (%s, %s, %s, %s)
            RETURNING author_id
        """, (first_name, last_name, birth_year, country))
        author_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Added author with ID: {author_id}")
        return author_id

def search_books(search_term):
    """Search for books by title"""
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT b.title, a.first_name || ' ' || a.last_name AS author,
                   b.publication_year, b.available_copies
            FROM books b
            JOIN authors a ON b.author_id = a.author_id
            WHERE b.title ILIKE %s
        """, (f'%{search_term}%',))
        return cursor.fetchall()

def borrow_book(member_id, book_id):
    """Record a book borrowing"""
    with conn.cursor() as cursor:
        # Check if book is available
        cursor.execute(
            "SELECT available_copies FROM books WHERE book_id = %s",
            (book_id,)
        )
        copies = cursor.fetchone()[0]

        if copies > 0:
            # Create borrowing record
            cursor.execute("""
                INSERT INTO borrowings (book_id, member_id, borrow_date, due_date)
                VALUES (%s, %s, CURRENT_DATE, CURRENT_DATE + INTERVAL '14 days')
            """, (book_id, member_id))

            # Update available copies
            cursor.execute("""
                UPDATE books
                SET available_copies = available_copies - 1
                WHERE book_id = %s
            """, (book_id,))

            conn.commit()
            print(f"Book borrowed successfully")
            return True
        else:
            print("No copies available")
            return False

# Test the functions
if __name__ == "__main__":
    # Add a new author
    add_author("Jane", "Austen", 1775, "United Kingdom")

    # Search for books
    results = search_books("Harry")
    for book in results:
        print(f"{book['title']} by {book['author']}")

    # Borrow a book
    borrow_book(member_id=1, book_id=1)

    # Close connection
    conn.close()
```

### Tasks:
1. Run the script and verify it works
2. Add error handling (try/except blocks)
3. Add a function to return a book
4. Add a function to list overdue books
5. Add a function to get member borrowing history

### Expected Outcome
You should be comfortable connecting to PostgreSQL from Python and performing database operations programmatically.

---

## Challenge Exercises

Once you've completed the basic exercises, try these challenges:

### Challenge 1: Overdue Books Report
Write a query that shows:
- Member name
- Book title
- Days overdue
- Only for books that are currently overdue (not yet returned)

### Challenge 2: Popular Authors Report
Create a query that ranks authors by:
- Total books written
- Total times their books have been borrowed
- Current availability of their books

### Challenge 3: Library Statistics
Write queries to calculate:
- Total number of books in the library
- Total number of available books
- Most popular genre
- Average book length by genre
- Percentage of books currently borrowed

### Challenge 4: Build a Complete Library Management System
Create a Python command-line application with:
- Menu-driven interface
- Functions for all library operations (add, search, borrow, return)
- Input validation
- Error handling
- Transaction management

---

## Verification and Testing

After completing each exercise:

1. **Verify your queries return expected results**
2. **Check data integrity** (foreign keys, constraints)
3. **Test edge cases** (empty results, invalid inputs)
4. **Review query performance** (use EXPLAIN)

## Common Mistakes to Avoid

1. **Forgetting WHERE clauses** in UPDATE/DELETE (affects all rows!)
2. **Not checking foreign key constraints** before deleting
3. **Comparing NULL with = instead of IS NULL**
4. **Not committing transactions** in Python
5. **SQL injection** (always use parameterized queries)

## Additional Resources

- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [SQL Practice Problems](https://www.sql-practice.com/)
- [Python psycopg2 Documentation](https://www.psycopg.org/docs/)

## Next Steps

Once you've mastered these beginner exercises:
1. Move on to [Intermediate Exercises](../intermediate/README.md)
2. Explore [Advanced SQL Concepts](../../02-relational-databases/introduction.md)
3. Learn about [Performance Optimization](../../09-performance/README.md)

---

**Need Help?**
- Review the [Fundamentals](../../01-fundamentals/README.md) section
- Check the [Code Examples](../../examples/python/)
- Refer to the [PostgreSQL Guide](../../02-relational-databases/postgresql/README.md)

Happy coding! 🎓
