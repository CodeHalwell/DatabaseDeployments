# Part 2: Relational Databases

## Overview

Relational databases have been the backbone of data management for over four decades. They organize data into tables with predefined relationships and use SQL (Structured Query Language) for data manipulation. This section provides comprehensive coverage of major relational database systems and SQL best practices.

## What You'll Learn

- SQL fundamentals and advanced concepts
- PostgreSQL: Open-source powerhouse
- MySQL: Web application favorite
- Microsoft SQL Server: Enterprise features
- Oracle Database: Maximum scalability
- Best practices for relational database design
- When to choose relational over NoSQL

## Why Relational Databases?

### Core Strengths

1. **ACID Compliance**: Guaranteed transaction reliability
2. **Data Integrity**: Enforced constraints and referential integrity
3. **Powerful Querying**: Complex joins, aggregations, and subqueries
4. **Mature Ecosystem**: Decades of tools, libraries, and best practices
5. **Standardization**: SQL is an industry standard

### When to Use Relational Databases

- Financial systems requiring ACID guarantees
- Applications with complex relationships
- Structured data with clear schema
- Need for complex queries and reporting
- Multi-row transactions
- Strong consistency requirements

### When to Consider Alternatives

- Rapidly changing schemas
- Massive horizontal scale (billions of records)
- Simple key-value lookups
- Unstructured or semi-structured data
- Eventually consistent data acceptable

## SQL Fundamentals

### Data Definition Language (DDL)

```sql
-- Create database
CREATE DATABASE company_db;

-- Create table with constraints
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    salary DECIMAL(10, 2) CHECK (salary > 0),
    department_id INTEGER REFERENCES departments(department_id),
    manager_id INTEGER REFERENCES employees(employee_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_email ON employees(email);
CREATE INDEX idx_employees_hire_date ON employees(hire_date);

-- Add constraints
ALTER TABLE employees
ADD CONSTRAINT check_hire_date CHECK (hire_date <= CURRENT_DATE);

-- Modify table
ALTER TABLE employees ADD COLUMN phone VARCHAR(20);
ALTER TABLE employees DROP COLUMN phone;
```

### Data Manipulation Language (DML)

```sql
-- INSERT
INSERT INTO employees (first_name, last_name, email, salary, department_id)
VALUES ('John', 'Doe', 'john.doe@company.com', 75000, 1);

-- Multiple inserts
INSERT INTO employees (first_name, last_name, email, salary, department_id)
VALUES
    ('Jane', 'Smith', 'jane.smith@company.com', 80000, 2),
    ('Bob', 'Johnson', 'bob.johnson@company.com', 70000, 1),
    ('Alice', 'Williams', 'alice.williams@company.com', 90000, 3);

-- UPDATE
UPDATE employees
SET salary = salary * 1.1
WHERE department_id = 1 AND hire_date < '2023-01-01';

-- DELETE
DELETE FROM employees
WHERE employee_id = 100;

-- SELECT
SELECT
    e.first_name,
    e.last_name,
    e.salary,
    d.department_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
WHERE e.salary > 70000
ORDER BY e.salary DESC
LIMIT 10;
```

### Advanced Queries

```sql
-- Subqueries
SELECT first_name, last_name, salary
FROM employees
WHERE salary > (
    SELECT AVG(salary)
    FROM employees
    WHERE department_id = employees.department_id
);

-- Common Table Expressions (CTE)
WITH department_stats AS (
    SELECT
        department_id,
        COUNT(*) as employee_count,
        AVG(salary) as avg_salary,
        MAX(salary) as max_salary
    FROM employees
    GROUP BY department_id
)
SELECT
    d.department_name,
    ds.employee_count,
    ds.avg_salary,
    ds.max_salary
FROM department_stats ds
JOIN departments d ON ds.department_id = d.department_id
WHERE ds.employee_count > 5;

-- Window Functions
SELECT
    first_name,
    last_name,
    department_id,
    salary,
    AVG(salary) OVER (PARTITION BY department_id) as dept_avg_salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_rank,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as overall_rank
FROM employees;

-- Recursive Queries (org chart)
WITH RECURSIVE org_chart AS (
    -- Base case: top-level managers
    SELECT
        employee_id,
        first_name,
        last_name,
        manager_id,
        1 as level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: employees reporting to managers
    SELECT
        e.employee_id,
        e.first_name,
        e.last_name,
        e.manager_id,
        oc.level + 1
    FROM employees e
    INNER JOIN org_chart oc ON e.manager_id = oc.employee_id
)
SELECT * FROM org_chart ORDER BY level, last_name;
```

## Database Design Principles

### Normalization

**First Normal Form (1NF)**: Atomic values
```sql
-- Bad: Multiple values in one column
CREATE TABLE orders (
    order_id INT,
    products VARCHAR(200)  -- 'Laptop, Mouse, Keyboard'
);

-- Good: Separate rows for each value
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT
);
```

**Second Normal Form (2NF)**: No partial dependencies
```sql
-- Bad: Non-key attributes depend on part of composite key
CREATE TABLE order_details (
    order_id INT,
    product_id INT,
    product_name VARCHAR(100),  -- Depends only on product_id
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);

-- Good: Separate tables
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

**Third Normal Form (3NF)**: No transitive dependencies
```sql
-- Bad: Non-key attribute depends on another non-key attribute
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    department_name VARCHAR(100)  -- Depends on department_id, not employee_id
);

-- Good: Separate department information
CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100)
);

CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);
```

### Denormalization (When Appropriate)

```sql
-- Sometimes denormalization improves read performance
-- Trade-off: Storage and update complexity vs. query speed

CREATE TABLE order_summary (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    order_date DATE,
    total_amount DECIMAL(10,2),
    item_count INT,
    -- Denormalized: Could be calculated from order_items
    -- But stored for faster dashboard queries
    status VARCHAR(20)
);
```

## Section Contents

### [Introduction to SQL and Relational Concepts](./introduction.md)
Comprehensive guide to SQL fundamentals, relational theory, and database design principles.

### [PostgreSQL](./postgresql/README.md)
**The world's most advanced open-source relational database**

Topics covered:
- Installation and setup
- Core features and capabilities
- Advanced data types (JSON, Arrays, PostGIS)
- Performance tuning
- Replication and high availability
- Python connectivity examples

### [MySQL](./mysql/README.md)
**The most popular open-source database for web applications**

Topics covered:
- Installation and configuration
- Storage engines (InnoDB, MyISAM)
- Query optimization
- Replication strategies
- Python connectivity examples
- Common use cases

### [Microsoft SQL Server](./sqlserver/README.md)
**Enterprise-grade database with Windows ecosystem integration**

Topics covered:
- Installation and setup
- T-SQL specifics
- Integration Services (SSIS)
- Reporting Services (SSRS)
- High availability features
- Python connectivity examples

### [Oracle Database](./oracle/README.md)
**Maximum performance and scalability for enterprises**

Topics covered:
- Oracle architecture
- PL/SQL programming
- Advanced features (RAC, Data Guard)
- Partitioning strategies
- Python connectivity examples
- Enterprise deployment

### [SQL Best Practices](./sql-best-practices.md)
Industry best practices for SQL development, optimization, and maintenance.

## Quick Comparison Matrix

| Feature | PostgreSQL | MySQL | SQL Server | Oracle |
|---------|-----------|-------|------------|--------|
| **License** | Open Source (PostgreSQL) | Open Source (GPL) / Commercial | Commercial | Commercial |
| **Cost** | Free | Free (Community) / Paid (Enterprise) | $$ | $$$$ |
| **Platform** | Cross-platform | Cross-platform | Windows (primary), Linux | Cross-platform |
| **ACID Compliance** | Yes | Yes (InnoDB) | Yes | Yes |
| **JSON Support** | Excellent | Good | Good | Good |
| **Scalability** | Excellent | Very Good | Excellent | Excellent |
| **Replication** | Built-in | Built-in | Built-in | Advanced (RAC) |
| **Best For** | General purpose, complex queries | Web applications, read-heavy | Windows ecosystem, BI | Large enterprises, maximum scale |
| **Learning Curve** | Medium | Easy | Medium | Steep |

## Choosing Between Relational Databases

### PostgreSQL: Choose When
- Need advanced features (JSON, full-text search, geospatial)
- Complex queries and data types
- Open-source requirement
- Strong standards compliance important
- **Example**: SaaS applications, analytics platforms

### MySQL: Choose When
- Simple, proven technology needed
- Read-heavy web applications
- Cost is a concern
- Large community support desired
- **Example**: WordPress, content websites, startups

### SQL Server: Choose When
- Windows ecosystem integration required
- .NET application stack
- Advanced BI and reporting needed
- Enterprise support required
- **Example**: Corporate applications, .NET backends

### Oracle: Choose When
- Maximum performance and scalability required
- Mission-critical enterprise application
- Advanced features needed (RAC, partitioning)
- Budget allows enterprise-grade solution
- **Example**: Banking systems, large ERP systems

## Learning Path

### Beginner Path
1. Start with [SQL Introduction](./introduction.md)
2. Set up [PostgreSQL](./postgresql/README.md) locally
3. Practice basic CRUD operations
4. Learn [SQL Best Practices](./sql-best-practices.md)
5. Connect to database from [Python](../05-backend-connectivity/python/postgresql.md)

### Intermediate Path
1. Study advanced SQL (joins, subqueries, CTEs)
2. Explore [MySQL](./mysql/README.md) and compare with PostgreSQL
3. Learn about indexes and query optimization
4. Practice database design and normalization
5. Implement [migrations](../07-migrations/README.md)

### Advanced Path
1. Study [SQL Server](./sqlserver/README.md) enterprise features
2. Explore [Oracle](./oracle/README.md) for maximum scale
3. Master [performance optimization](../09-performance/README.md)
4. Learn [replication and scaling](../11-scaling/README.md)
5. Implement [production deployment](../08-deployment/README.md)

## Hands-On Exercises

### Exercise 1: Design a Blog Database
Create a normalized schema for a blogging platform with users, posts, comments, and tags.

### Exercise 2: Complex Queries
Write queries to:
- Find top 10 most commented posts
- Calculate average comments per user
- Find posts with multiple tags
- Generate monthly posting statistics

### Exercise 3: Performance Optimization
- Add appropriate indexes
- Analyze query plans
- Optimize slow queries
- Measure performance improvements

### Exercise 4: Data Migration
- Export data from one database
- Transform data structure
- Import into new schema
- Verify data integrity

## Common Patterns

### Pagination
```sql
-- Efficient pagination
SELECT * FROM posts
ORDER BY created_at DESC
LIMIT 20 OFFSET 40;  -- Page 3 (20 items per page)

-- Better for large offsets (keyset pagination)
SELECT * FROM posts
WHERE created_at < :last_seen_timestamp
ORDER BY created_at DESC
LIMIT 20;
```

### Soft Deletes
```sql
-- Add deleted_at column
ALTER TABLE posts ADD COLUMN deleted_at TIMESTAMP;

-- "Delete" by setting timestamp
UPDATE posts SET deleted_at = NOW() WHERE post_id = 123;

-- Query only active records
SELECT * FROM posts WHERE deleted_at IS NULL;
```

### Audit Trails
```sql
-- Create audit table
CREATE TABLE posts_audit (
    audit_id SERIAL PRIMARY KEY,
    post_id INT,
    action VARCHAR(10),
    old_data JSONB,
    new_data JSONB,
    changed_by INT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to populate audit table
CREATE OR REPLACE FUNCTION audit_posts()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        INSERT INTO posts_audit (post_id, action, old_data, new_data, changed_by)
        VALUES (NEW.post_id, 'UPDATE', row_to_json(OLD), row_to_json(NEW), current_user_id());
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO posts_audit (post_id, action, old_data, changed_by)
        VALUES (OLD.post_id, 'DELETE', row_to_json(OLD), current_user_id());
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER posts_audit_trigger
AFTER UPDATE OR DELETE ON posts
FOR EACH ROW EXECUTE FUNCTION audit_posts();
```

## Next Steps

1. **Start Learning**: Begin with [SQL Introduction](./introduction.md)
2. **Get Hands-On**: Set up [PostgreSQL locally](./postgresql/README.md)
3. **Connect to Apps**: Learn [Python connectivity](../05-backend-connectivity/python/postgresql.md)
4. **Go Deeper**: Explore [Performance Optimization](../09-performance/README.md)

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [SQL Server Documentation](https://docs.microsoft.com/en-us/sql/)
- [Oracle Documentation](https://docs.oracle.com/en/database/)
- [SQL Tutorial (W3Schools)](https://www.w3schools.com/sql/)
- [Mode Analytics SQL Tutorial](https://mode.com/sql-tutorial/)

---

[← Previous: Fundamentals](../01-fundamentals/README.md) | [Next: PostgreSQL →](./postgresql/README.md)
