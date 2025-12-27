# What Are Databases?

## Introduction

A **database** is an organized collection of structured data stored electronically in a computer system. Databases are managed by Database Management Systems (DBMS), which provide interfaces for creating, reading, updating, and deleting data (CRUD operations).

## Definition and Core Concepts

### What is a Database?

At its simplest, a database is a systematic collection of data that:
- **Organized**: Data is structured in a meaningful way
- **Persistent**: Data survives beyond the lifetime of the program that created it
- **Accessible**: Data can be efficiently retrieved and manipulated
- **Shareable**: Multiple users/applications can access data concurrently
- **Secure**: Access can be controlled and data can be protected

### Database Management System (DBMS)

A DBMS is software that interacts with end users, applications, and the database itself to capture and analyze data. Key functions include:

1. **Data Definition**: Creating and modifying database structures
2. **Data Manipulation**: Inserting, updating, deleting, and querying data
3. **Data Security**: Controlling access and ensuring data integrity
4. **Data Recovery**: Backup and restoration capabilities
5. **Concurrency Control**: Managing simultaneous access by multiple users

## History and Evolution

### Early Days (1960s-1970s)
- **Hierarchical Databases**: Tree-like structures (e.g., IBM's IMS)
- **Network Databases**: More flexible relationships (e.g., CODASYL)
- Limited by rigid structures and complex navigation

### The Relational Revolution (1970s-1980s)
- **Edgar F. Codd** introduced the relational model (1970)
- Data organized in tables with relationships
- **SQL** (Structured Query Language) becomes the standard
- Examples: Oracle, IBM DB2, Microsoft SQL Server

### Object-Oriented Era (1990s)
- Integration of object-oriented programming concepts
- Object-relational databases emerge
- Better support for complex data types

### NoSQL Movement (2000s-Present)
- Rise of web-scale applications
- Need for horizontal scalability
- Document stores, key-value stores, wide-column stores
- Examples: MongoDB, Cassandra, Redis

### NewSQL and Beyond (2010s-Present)
- Combining SQL benefits with NoSQL scalability
- Distributed SQL databases
- Cloud-native databases
- Examples: Google Spanner, CockroachDB

## Database vs. File Systems

### Why Not Just Use Files?

While simple file storage seems sufficient, databases offer critical advantages:

| Feature | File System | Database |
|---------|-------------|----------|
| **Data Structure** | Unstructured or loosely structured | Highly structured with schemas |
| **Concurrent Access** | Limited, prone to conflicts | Built-in concurrency control |
| **Data Integrity** | Manual validation required | Automatic constraint enforcement |
| **Querying** | Must parse entire files | Optimized query engines |
| **Relationships** | Manual linking | Built-in relationship management |
| **Transactions** | Not supported | ACID compliance |
| **Security** | File-level permissions | Row/column level access control |
| **Scalability** | Limited | Designed for scale |

### Example Scenario

**File-based approach:**
```python
# Reading user data from a JSON file
import json

with open('users.json', 'r') as f:
    users = json.load(f)

# Finding a user (requires iterating through all users)
target_user = None
for user in users:
    if user['email'] == 'john@example.com':
        target_user = user
        break
```

**Database approach:**
```python
# Using SQL database
import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Efficient indexed lookup
cursor.execute("SELECT * FROM users WHERE email = ?", ('john@example.com',))
target_user = cursor.fetchone()
```

## ACID Properties

ACID is a set of properties that guarantee reliable database transactions:

### A - Atomicity
**"All or nothing"** - A transaction must complete entirely or not at all.

**Example:**
```sql
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- If any statement fails, entire transaction rolls back
```

### C - Consistency
**"Rules are preserved"** - Data must be valid according to defined rules and constraints.

**Example:**
```sql
-- Constraint ensures balance never goes negative
ALTER TABLE accounts ADD CONSTRAINT positive_balance
    CHECK (balance >= 0);
```

### I - Isolation
**"Concurrent transactions don't interfere"** - Transactions execute as if they're alone.

**Example:**
```
Transaction 1: Read balance = $100
Transaction 2: Read balance = $100
Transaction 1: Write balance = $150
Transaction 2: Write balance = $50  -- Without isolation, this overwrites T1's changes
```

### D - Durability
**"Committed data persists"** - Once committed, data survives system failures.

**Example:**
```sql
COMMIT;  -- After this, data is guaranteed to persist even if system crashes
```

## CAP Theorem

The CAP theorem states that a distributed database system can only guarantee two of three properties:

### C - Consistency
All nodes see the same data at the same time.

### A - Availability
Every request receives a response (success or failure).

### P - Partition Tolerance
System continues operating despite network partitions.

### Trade-offs

```
┌─────────────────────────────────────────┐
│         CAP Theorem Triangle            │
│                                         │
│              Consistency                │
│                   /\                    │
│                  /  \                   │
│                 /    \                  │
│                /  CA  \                 │
│               /  (RDBMS)\               │
│              /____________\             │
│             /      |       \            │
│            /   CP  |   AP   \           │
│           /  (HBase)| (Cassandra)\      │
│          /________|_________\          │
│    Partition              Availability  │
│    Tolerance                            │
└─────────────────────────────────────────┘
```

**Examples:**
- **CP**: MongoDB, HBase, Redis (prioritize consistency and partition tolerance)
- **AP**: Cassandra, DynamoDB, CouchDB (prioritize availability and partition tolerance)
- **CA**: PostgreSQL, MySQL (traditional RDBMS, assume no network partitions)

## Key Database Concepts

### Schema
A schema defines the structure of a database:
- **Tables/Collections**: Container for data
- **Columns/Fields**: Individual data elements
- **Data Types**: Integer, String, Date, etc.
- **Constraints**: Rules for data validity

```sql
-- Example schema
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
Structures that improve query performance:

```sql
-- Create index for faster lookups
CREATE INDEX idx_users_email ON users(email);

-- Query now uses index for O(log n) lookup instead of O(n) scan
SELECT * FROM users WHERE email = 'john@example.com';
```

### Transactions
Logical units of work that ensure data integrity:

```python
# Python example with transaction
conn.begin()
try:
    cursor.execute("UPDATE account SET balance = balance - 100 WHERE id = 1")
    cursor.execute("UPDATE account SET balance = balance + 100 WHERE id = 2")
    conn.commit()  # All operations succeed
except Exception as e:
    conn.rollback()  # Any failure rolls back all changes
    print(f"Transaction failed: {e}")
```

### Normalization
Process of organizing data to reduce redundancy:

**Unnormalized:**
```
Orders
| OrderID | CustomerName | CustomerEmail | ProductName | Price |
|---------|--------------|---------------|-------------|-------|
| 1       | John Doe     | john@ex.com   | Laptop      | 1000  |
| 2       | John Doe     | john@ex.com   | Mouse       | 20    |
```

**Normalized:**
```
Customers
| CustomerID | Name     | Email       |
|------------|----------|-------------|
| 1          | John Doe | john@ex.com |

Orders
| OrderID | CustomerID | ProductID |
|---------|------------|-----------|
| 1       | 1          | 1         |
| 2       | 1          | 2         |

Products
| ProductID | Name   | Price |
|-----------|--------|-------|
| 1         | Laptop | 1000  |
| 2         | Mouse  | 20    |
```

## Modern Database Landscape

### Cloud Databases
- Managed services (AWS RDS, Azure SQL Database)
- Serverless databases (Amazon Aurora Serverless)
- Reduced operational overhead

### Multi-Model Databases
- Support multiple data models (document, graph, key-value)
- Examples: ArangoDB, CosmosDB

### Time-Series Databases
- Optimized for time-stamped data
- Examples: InfluxDB, TimescaleDB
- Use cases: IoT, monitoring, financial data

### Graph Databases
- Optimized for relationship-heavy data
- Examples: Neo4j, Amazon Neptune
- Use cases: Social networks, recommendation engines

## Summary

Databases are foundational to modern software development because they provide:
- **Structured data storage** with efficient access patterns
- **ACID guarantees** for reliable transactions
- **Concurrent access** with proper isolation
- **Scalability** for growing data needs
- **Security** and access control
- **Query optimization** for performance

Understanding these fundamental concepts prepares you for choosing and working with specific database technologies covered in subsequent sections.

## Key Takeaways

1. Databases are more than file storage - they provide structure, security, and performance
2. ACID properties ensure transaction reliability
3. CAP theorem explains trade-offs in distributed systems
4. Different database types have evolved to meet different needs
5. Modern applications often use multiple database types

## Next Steps

- [Database Types and Categories](./database-types.md) - Explore different database types
- [Why Databases Matter](./why-databases-matter.md) - Learn about real-world impacts
- [Choosing the Right Database](./choosing-database.md) - Make informed decisions

## Practice Questions

1. What are the four ACID properties and why is each important?
2. Explain the CAP theorem and give examples of databases in each category.
3. Why would you use a database instead of JSON files for an application?
4. What is the difference between a database and a DBMS?
5. How has the database landscape evolved over the past 50 years?

---

[← Back to Fundamentals](./README.md) | [Next: Database Types →](./database-types.md)
