# Python Database Connectivity (Primary Focus)

## Overview

Python is one of the most popular languages for backend development, with excellent database connectivity libraries for both SQL and NoSQL databases. This comprehensive guide covers connecting Python applications to various databases, with practical examples and best practices.

## Why Python for Database Applications?

### Advantages

1. **Rich Ecosystem**: Comprehensive libraries for all major databases
2. **Easy to Learn**: Simple syntax and readable code
3. **Versatile**: Web frameworks, APIs, data science, automation
4. **Strong Typing Support**: Type hints for safer code
5. **Excellent ORMs**: SQLAlchemy, Django ORM, Tortoise ORM
6. **Async Support**: AsyncIO for high-performance applications

### Popular Python Database Libraries

| Database | Libraries | Use Case |
|----------|-----------|----------|
| **PostgreSQL** | psycopg2, asyncpg, SQLAlchemy | Most versatile relational DB |
| **MySQL** | mysql-connector-python, PyMySQL, mysqlclient | Web applications, WordPress backends |
| **MongoDB** | pymongo, motor, mongoengine | Flexible schemas, rapid development |
| **Redis** | redis-py, aioredis | Caching, session storage, queues |
| **Cassandra** | cassandra-driver | High-volume writes, time-series |
| **DynamoDB** | boto3 | AWS ecosystem, serverless |
| **SQLite** | sqlite3 (built-in) | Local development, embedded apps |

## Contents

This section provides comprehensive coverage of Python database connectivity:

### Core Topics

1. **[PostgreSQL with Python](./postgresql.md)**
   - psycopg2 for synchronous operations
   - asyncpg for async/await patterns
   - SQLAlchemy ORM
   - Connection pooling
   - Query optimization
   - Real-world examples

2. **[MySQL with Python](./mysql.md)**
   - mysql-connector-python
   - PyMySQL
   - SQLAlchemy with MySQL
   - Performance considerations
   - Migration from MySQL to PostgreSQL

3. **[MongoDB with Python](./mongodb.md)**
   - pymongo basics
   - Motor for async operations
   - MongoEngine ODM
   - Aggregation pipelines
   - Indexing strategies

4. **[Redis with Python](./redis.md)**
   - redis-py fundamentals
   - Data structures (strings, hashes, lists, sets, sorted sets)
   - Pub/Sub patterns
   - Caching strategies
   - Session management

5. **[Advanced Python Patterns](./advanced-patterns.md)**
   - Connection pooling
   - Transaction management
   - Repository pattern
   - Unit of Work pattern
   - Database factories
   - Testing strategies
   - Async vs sync considerations

## Quick Start Examples

### PostgreSQL with psycopg2

```python
import psycopg2
from psycopg2.extras import RealDictCursor

# Connect to database
conn = psycopg2.connect(
    dbname="myapp",
    user="postgres",
    password="password",
    host="localhost",
    port=5432
)

# Create cursor
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Execute query
cursor.execute("""
    SELECT id, username, email
    FROM users
    WHERE created_at > %s
    ORDER BY created_at DESC
    LIMIT %s
""", ('2024-01-01', 10))

# Fetch results
users = cursor.fetchall()
for user in users:
    print(f"{user['username']}: {user['email']}")

# Close connections
cursor.close()
conn.close()
```

### MongoDB with pymongo

```python
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['myapp']
users = db['users']

# Insert document
user_id = users.insert_one({
    'username': 'johndoe',
    'email': 'john@example.com',
    'created_at': datetime.utcnow(),
    'profile': {
        'first_name': 'John',
        'last_name': 'Doe',
        'age': 30
    },
    'tags': ['active', 'premium']
}).inserted_id

# Query documents
active_users = users.find({
    'tags': 'active',
    'profile.age': {'$gte': 18}
}).limit(10)

for user in active_users:
    print(user['username'])
```

### Redis for Caching

```python
import redis
import json
from functools import wraps

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def cache_result(expiration=3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Try to get from cache
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            r.setex(cache_key, expiration, json.dumps(result))

            return result
        return wrapper
    return decorator

@cache_result(expiration=300)  # Cache for 5 minutes
def get_user_profile(user_id):
    # Expensive database query
    # This result will be cached
    return fetch_from_database(user_id)
```

## Database Connection Patterns

### 1. Direct Connection (Simple)

```python
import psycopg2

def get_user(user_id):
    conn = psycopg2.connect(
        dbname="myapp",
        user="postgres",
        password="password"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Problem: Creates new connection for each request
# Not efficient for production
```

### 2. Connection Pooling (Production)

```python
from psycopg2 import pool

# Create connection pool
db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname="myapp",
    user="postgres",
    password="password"
)

def get_user(user_id):
    # Get connection from pool
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return user
    finally:
        # Return connection to pool
        db_pool.putconn(conn)

# Much more efficient: Reuses connections
```

### 3. Context Manager (Best Practice)

```python
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = db_pool.getconn()
    try:
        yield conn
        conn.commit()  # Auto-commit on success
    except Exception:
        conn.rollback()  # Auto-rollback on error
        raise
    finally:
        db_pool.putconn(conn)

def get_user(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()

# Clean, safe, and efficient
```

### 4. ORM Approach (SQLAlchemy)

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Setup
engine = create_engine('postgresql://user:password@localhost/myapp')
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

# Query
def get_user(user_id):
    session = Session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        return user
    finally:
        session.close()

# High-level, database-agnostic, with relationship management
```

## Async vs Sync

### When to Use Async

**Use async when:**
- High concurrency (1000+ simultaneous requests)
- I/O-bound operations dominate
- Using async web frameworks (FastAPI, Sanic)
- Real-time applications (WebSockets)

**Example: Async PostgreSQL**
```python
import asyncpg
import asyncio

async def get_users():
    # Create connection pool
    pool = await asyncpg.create_pool(
        'postgresql://user:password@localhost/myapp',
        min_size=10,
        max_size=20
    )

    # Use connection from pool
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM users WHERE active = $1', True)
        return [dict(row) for row in rows]

# Run async function
users = asyncio.run(get_users())
```

### When to Use Sync

**Use sync when:**
- Simple CRUD applications
- Low to medium concurrency
- Synchronous frameworks (Flask, Django)
- Easier debugging and testing
- Team familiarity

**Example: Sync PostgreSQL**
```python
import psycopg2

def get_users():
    conn = psycopg2.connect(
        dbname="myapp",
        user="postgres",
        password="password"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE active = %s", (True,))
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

# Simpler, more straightforward
```

## Error Handling Best Practices

### Comprehensive Error Handling

```python
import psycopg2
from psycopg2 import sql, OperationalError, IntegrityError
import logging

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Base exception for database operations"""
    pass

class ConnectionError(DatabaseError):
    """Connection-related errors"""
    pass

class QueryError(DatabaseError):
    """Query execution errors"""
    pass

def safe_query(query, params=None):
    """Execute query with comprehensive error handling"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise ConnectionError("Could not connect to database") from e

    except IntegrityError as e:
        logger.error(f"Data integrity error: {e}")
        raise QueryError("Data integrity violation") from e

    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        raise DatabaseError("Database operation failed") from e

# Usage
try:
    users = safe_query("SELECT * FROM users WHERE id = %s", (user_id,))
except ConnectionError:
    # Handle connection issues (retry, fallback)
    pass
except QueryError:
    # Handle data issues (validation error)
    pass
```

## Security Best Practices

### 1. Never Use String Formatting for Queries

```python
# ❌ VULNERABLE TO SQL INJECTION
def get_user_bad(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)  # DON'T DO THIS!

# Attacker input: "' OR '1'='1"
# Results in: SELECT * FROM users WHERE username = '' OR '1'='1'
# Returns all users!

# ✅ SAFE: Use parameterized queries
def get_user_safe(username):
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))  # Safe from injection
```

### 2. Use Environment Variables for Credentials

```python
import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# ✅ Safe: Credentials from environment
DATABASE_URL = os.getenv('DATABASE_URL')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=DB_USER,
    password=DB_PASSWORD,
    host=os.getenv('DB_HOST', 'localhost')
)

# ❌ Never hardcode credentials in source code
# conn = psycopg2.connect(
#     dbname="myapp",
#     user="admin",
#     password="secretpassword123"  # DON'T DO THIS!
# )
```

### 3. Implement Connection Timeout

```python
import psycopg2

try:
    conn = psycopg2.connect(
        dbname="myapp",
        user="postgres",
        password="password",
        host="localhost",
        connect_timeout=5  # Timeout after 5 seconds
    )
except psycopg2.OperationalError:
    # Handle timeout
    logger.error("Database connection timeout")
```

## Performance Optimization

### 1. Use Connection Pooling

```python
from psycopg2 import pool

# Create pool once at application startup
db_pool = pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    dbname="myapp",
    user="postgres",
    password="password"
)

# Benefits:
# - Reuse connections (no setup/teardown overhead)
# - Limit concurrent connections
# - Better resource utilization
```

### 2. Batch Operations

```python
# ❌ Inefficient: Multiple individual inserts
for user in users:
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        (user['name'], user['email'])
    )
    conn.commit()  # Commit each insert

# ✅ Efficient: Batch insert
from psycopg2.extras import execute_batch

execute_batch(
    cursor,
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    [(user['name'], user['email']) for user in users]
)
conn.commit()  # Single commit

# Can be 10-100x faster for large datasets
```

### 3. Use Proper Indexing

```python
# Create index for frequently queried columns
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_users_email
    ON users(email);
""")

# Query using indexed column
cursor.execute("""
    SELECT * FROM users WHERE email = %s
""", (email,))

# Query plan shows index usage:
# Index Scan using idx_users_email (cost=0.28..8.29)
# vs
# Seq Scan on users (cost=0.00..35.50)  # Without index
```

## Testing Database Code

### Unit Testing with Mocks

```python
import unittest
from unittest.mock import Mock, patch
import psycopg2

class TestUserQueries(unittest.TestCase):

    @patch('psycopg2.connect')
    def test_get_user(self, mock_connect):
        # Setup mock
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, 'john', 'john@example.com')

        # Test function
        user = get_user(1)

        # Assertions
        mock_cursor.execute.assert_called_once()
        self.assertEqual(user[0], 1)
        self.assertEqual(user[1], 'john')
```

### Integration Testing with Test Database

```python
import pytest
import psycopg2

@pytest.fixture
def test_db():
    """Create test database"""
    conn = psycopg2.connect(
        dbname="test_myapp",
        user="postgres",
        password="password"
    )

    # Setup: Create tables
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50),
            email VARCHAR(100)
        )
    """)
    conn.commit()

    yield conn

    # Teardown: Clean up
    cursor.execute("DROP TABLE users")
    conn.commit()
    conn.close()

def test_insert_user(test_db):
    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO users (username, email) VALUES (%s, %s)",
        ('testuser', 'test@example.com')
    )
    test_db.commit()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    assert count == 1
```

## Real-World Application Example

### Complete Flask API with PostgreSQL

```python
from flask import Flask, request, jsonify
from psycopg2 import pool
from contextlib import contextmanager
import os

app = Flask(__name__)

# Initialize connection pool
db_pool = pool.SimpleConnectionPool(
    1, 10,
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST')
)

@contextmanager
def get_db_connection():
    conn = db_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)

# GET /users - List all users
@app.route('/users', methods=['GET'])
def get_users():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM users")
        users = [
            {'id': row[0], 'username': row[1], 'email': row[2]}
            for row in cursor.fetchall()
        ]
        return jsonify(users)

# GET /users/<id> - Get single user
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email FROM users WHERE id = %s",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            user = {'id': row[0], 'username': row[1], 'email': row[2]}
            return jsonify(user)
        return jsonify({'error': 'User not found'}), 404

# POST /users - Create user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id",
            (data['username'], data['email'])
        )
        user_id = cursor.fetchone()[0]
        return jsonify({'id': user_id, **data}), 201

# PUT /users/<id> - Update user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET username = %s, email = %s WHERE id = %s",
            (data['username'], data['email'], user_id)
        )
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'id': user_id, **data})

# DELETE /users/<id> - Delete user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404
        return '', 204

if __name__ == '__main__':
    app.run(debug=True)
```

## Summary

Python provides excellent database connectivity options:

- **psycopg2**: Battle-tested PostgreSQL adapter
- **asyncpg**: High-performance async PostgreSQL
- **SQLAlchemy**: Powerful ORM for multiple databases
- **pymongo**: Official MongoDB driver
- **redis-py**: Comprehensive Redis client

### Key Principles

1. Use connection pooling in production
2. Always use parameterized queries
3. Handle errors appropriately
4. Implement proper transaction management
5. Test database code thoroughly
6. Use environment variables for configuration
7. Choose async only when needed

## Next Steps

- [PostgreSQL with Python](./postgresql.md) - Deep dive into PostgreSQL connectivity
- [MongoDB with Python](./mongodb.md) - Work with document databases
- [Advanced Patterns](./advanced-patterns.md) - Production-ready patterns
- [Code Examples](../../examples/python/) - Complete working examples

---

[← Back to Backend Connectivity](../README.md) | [Next: PostgreSQL with Python →](./postgresql.md)
