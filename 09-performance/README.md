# Part 9: Performance Optimization

## Overview

Database performance is critical for application success. This section covers techniques to optimize query performance, reduce latency, and scale databases efficiently.

## What You'll Learn

- Understanding database performance metrics
- Query optimization techniques
- Indexing strategies
- Caching patterns
- Connection pooling
- Query profiling and monitoring
- Hardware considerations
- Real-world optimization examples

## Performance Fundamentals

### Key Performance Metrics

```
1. Throughput
   - Queries per second (QPS)
   - Transactions per second (TPS)
   - Read/write ratio

2. Latency
   - Query response time (p50, p95, p99)
   - Connection time
   - Lock wait time

3. Resource Utilization
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network bandwidth

4. Concurrency
   - Active connections
   - Blocked queries
   - Lock contention
```

### Performance Baselines

**What's "good" performance?**

| Operation | Target | Excellent | Poor |
|-----------|--------|-----------|------|
| Simple SELECT | <10ms | <5ms | >50ms |
| Complex query | <100ms | <50ms | >500ms |
| INSERT single | <5ms | <2ms | >20ms |
| UPDATE single | <10ms | <5ms | >50ms |
| Transaction | <50ms | <20ms | >200ms |

## Indexing Strategies

### Understanding Indexes

**Without Index (Table Scan):**
```
Query: SELECT * FROM users WHERE email = 'john@example.com'

Execution:
1. Read row 1 → Check email → No match
2. Read row 2 → Check email → No match
3. Read row 3 → Check email → No match
...
N. Read row 1,000,000 → Check email → Match!

Time: O(n) - Linear scan of all rows
```

**With Index (B-Tree Lookup):**
```
Query: SELECT * FROM users WHERE email = 'john@example.com'

Execution:
1. Look up 'john@example.com' in B-tree index → Row ID: 123,456
2. Read row 123,456 directly

Time: O(log n) - Logarithmic lookup
Result: 10,000x faster for 1M rows!
```

### Index Types

#### B-Tree Index (Default)

```sql
-- PostgreSQL/MySQL
CREATE INDEX idx_users_email ON users(email);

-- Best for:
-- - Equality lookups: WHERE email = 'john@example.com'
-- - Range queries: WHERE age BETWEEN 18 AND 65
-- - Sorting: ORDER BY created_at DESC
-- - Prefix matching: WHERE name LIKE 'John%'
```

#### Hash Index

```sql
-- PostgreSQL
CREATE INDEX idx_users_email_hash ON users USING HASH (email);

-- Best for:
-- - Equality lookups only: WHERE email = 'john@example.com'
-- - Faster than B-tree for equality
-- - Cannot handle range queries or sorting
```

#### GiN Index (Generalized Inverted Index)

```sql
-- PostgreSQL: Full-text search
CREATE INDEX idx_articles_content_gin ON articles
USING GIN (to_tsvector('english', content));

-- Query with full-text search
SELECT * FROM articles
WHERE to_tsvector('english', content) @@ to_tsquery('database & performance');

-- Best for:
-- - Full-text search
-- - Array containment: WHERE tags @> ARRAY['python']
-- - JSONB queries: WHERE data @> '{"status": "active"}'
```

#### Partial Index

```sql
-- Index only active users
CREATE INDEX idx_active_users_email ON users(email)
WHERE status = 'active';

-- Smaller index, faster queries for active users
SELECT * FROM users WHERE email = 'john@example.com' AND status = 'active';

-- Benefits:
-- - Smaller index size
-- - Faster updates (only updates when status = 'active')
-- - Lower maintenance cost
```

#### Composite Index

```sql
-- Index on multiple columns
CREATE INDEX idx_users_country_age ON users(country, age);

-- Efficient queries:
SELECT * FROM users WHERE country = 'USA' AND age = 30;  -- ✅ Uses index
SELECT * FROM users WHERE country = 'USA';                -- ✅ Uses index (leftmost)
SELECT * FROM users WHERE age = 30;                       -- ❌ Doesn't use index

-- Rule: Leftmost prefix must be in WHERE clause
```

### Index Best Practices

#### 1. Index Frequently Queried Columns

```python
# Analyze query patterns
slow_queries = """
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;
"""

# Common candidates for indexing:
# - Foreign keys
# - WHERE clause columns
# - ORDER BY columns
# - JOIN columns
```

#### 2. Don't Over-Index

```sql
-- ❌ Bad: Too many indexes
CREATE INDEX idx1 ON users(email);
CREATE INDEX idx2 ON users(username);
CREATE INDEX idx3 ON users(first_name);
CREATE INDEX idx4 ON users(last_name);
CREATE INDEX idx5 ON users(city);
CREATE INDEX idx6 ON users(state);
CREATE INDEX idx7 ON users(country);
-- ... (20 indexes)

-- Problem:
-- - Every INSERT/UPDATE must update 20 indexes
-- - Slows down writes significantly
-- - Increases storage requirements

-- ✅ Good: Strategic indexes based on query patterns
CREATE INDEX idx_users_email ON users(email);          -- Login queries
CREATE INDEX idx_users_country_city ON users(country, city);  -- Location searches
CREATE INDEX idx_users_created_at ON users(created_at);       -- Recent users
```

#### 3. Use EXPLAIN to Verify

```sql
-- PostgreSQL
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'john@example.com';

-- Output shows:
-- Index Scan using idx_users_email on users (cost=0.42..8.44 rows=1 width=100)
-- Planning Time: 0.123 ms
-- Execution Time: 0.045 ms

-- Look for:
-- ✅ "Index Scan" or "Index Only Scan" - Good!
-- ❌ "Seq Scan" (Sequential Scan) - Missing index!
-- ❌ High cost/execution time - Optimize query
```

```python
# Python: Explain query
cursor.execute("EXPLAIN ANALYZE SELECT * FROM users WHERE email = %s", ('john@example.com',))
plan = cursor.fetchall()
for line in plan:
    print(line[0])
```

#### 4. Index Coverage

```sql
-- Covering index: Includes all columns needed by query
CREATE INDEX idx_users_email_name ON users(email, username, first_name);

-- Index-only scan (doesn't need to read table)
SELECT username, first_name FROM users WHERE email = 'john@example.com';

-- Benefits:
-- - Faster: Only reads index, not table
-- - Less I/O
-- - Better cache utilization
```

### MongoDB Indexing

```python
from pymongo import ASCENDING, DESCENDING, TEXT

# Single field index
users.create_index([('email', ASCENDING)], unique=True)

# Compound index
users.create_index([
    ('country', ASCENDING),
    ('age', DESCENDING)
])

# Text index for full-text search
articles.create_index([('title', TEXT), ('content', TEXT)])

# Geospatial index
places.create_index([('location', '2dsphere')])

# TTL index (auto-delete old documents)
sessions.create_index('created_at', expireAfterSeconds=3600)

# Check index usage
users.aggregate([
    {'$indexStats': {}}
])

# Explain query
users.find({'email': 'john@example.com'}).explain()
```

## Query Optimization

### N+1 Query Problem

```python
# ❌ Bad: N+1 queries
users = db.query('SELECT * FROM users')
for user in users:
    orders = db.query('SELECT * FROM orders WHERE user_id = ?', user['id'])
    # 1 query for users + N queries for orders = N+1 queries!

# ✅ Good: JOIN or eager loading
results = db.query("""
    SELECT u.*, o.order_id, o.total
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
""")
# 1 query total!

# SQLAlchemy: Eager loading
users = session.query(User).options(
    joinedload(User.orders)
).all()
# Loads users and orders in one query
```

### SELECT Only Needed Columns

```python
# ❌ Bad: Select all columns
cursor.execute("SELECT * FROM users")  # Fetches all 20 columns

# ✅ Good: Select only needed columns
cursor.execute("SELECT id, username, email FROM users")  # Only 3 columns

# Benefits:
# - Less data transferred
# - Less memory used
# - Faster serialization
# - Better cache utilization

# MongoDB: Projection
users.find(
    {'status': 'active'},
    {'username': 1, 'email': 1, '_id': 0}  # Only fetch username and email
)
```

### Use LIMIT

```python
# ❌ Bad: Fetch all results
cursor.execute("SELECT * FROM articles ORDER BY created_at DESC")
articles = cursor.fetchall()  # Could be millions of rows!

# ✅ Good: Limit results
cursor.execute("SELECT * FROM articles ORDER BY created_at DESC LIMIT 20")
articles = cursor.fetchall()  # Only 20 rows

# Pagination: Use OFFSET (but see cursor-based pagination for better performance)
page = 1
per_page = 20
offset = (page - 1) * per_page

cursor.execute("""
    SELECT * FROM articles
    ORDER BY created_at DESC
    LIMIT %s OFFSET %s
""", (per_page, offset))
```

### Cursor-Based Pagination (Better Than OFFSET)

```python
# ❌ Bad: OFFSET for deep pagination
# SELECT * FROM articles ORDER BY id LIMIT 20 OFFSET 10000
# Problem: Database must scan 10,020 rows to return 20!

# ✅ Good: Cursor-based pagination
def get_articles(after_id=None, limit=20):
    """
    Cursor-based pagination using ID

    Args:
        after_id: Last ID from previous page (None for first page)
        limit: Number of results

    Returns:
        List of articles and next cursor
    """
    if after_id:
        query = """
            SELECT * FROM articles
            WHERE id > %s
            ORDER BY id
            LIMIT %s
        """
        cursor.execute(query, (after_id, limit))
    else:
        query = """
            SELECT * FROM articles
            ORDER BY id
            LIMIT %s
        """
        cursor.execute(query, (limit,))

    articles = cursor.fetchall()

    # Next cursor is the last ID
    next_cursor = articles[-1]['id'] if articles else None

    return articles, next_cursor

# Usage
articles, next_cursor = get_articles(limit=20)
# ... display articles ...

# Next page
articles, next_cursor = get_articles(after_id=next_cursor, limit=20)

# Benefits:
# - Consistent performance regardless of page depth
# - No missed or duplicate results
# - Works with infinite scroll
```

### Avoid Functions in WHERE Clause

```sql
-- ❌ Bad: Function prevents index usage
SELECT * FROM users WHERE LOWER(email) = 'john@example.com';
-- Can't use index on email!

-- ✅ Good: Use functional index or normalize data
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
SELECT * FROM users WHERE LOWER(email) = 'john@example.com';
-- Now uses index!

-- Or normalize email on insert
INSERT INTO users (email) VALUES (LOWER('John@Example.com'));
SELECT * FROM users WHERE email = 'john@example.com';
```

### Batch Operations

```python
# ❌ Bad: Individual inserts
for user in users:
    cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)",
                   (user['username'], user['email']))
    conn.commit()
# 1000 users = 1000 round trips!

# ✅ Good: Batch insert
from psycopg2.extras import execute_batch

execute_batch(
    cursor,
    "INSERT INTO users (username, email) VALUES (%s, %s)",
    [(u['username'], u['email']) for u in users]
)
conn.commit()
# 1000 users = 1 round trip!

# MongoDB: Bulk operations
from pymongo import InsertMany

users.insert_many([
    {'username': 'user1', 'email': 'user1@example.com'},
    {'username': 'user2', 'email': 'user2@example.com'},
    # ... 1000 documents
])
# Much faster than 1000 individual inserts
```

## Caching Strategies

### Cache-Aside Pattern

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_user(user_id):
    """
    Cache-aside pattern:
    1. Try cache
    2. On miss, query database
    3. Store in cache
    """
    cache_key = f'user:{user_id}'

    # Try cache
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss - query database
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        # Store in cache (1 hour TTL)
        r.setex(cache_key, 3600, json.dumps(user))

    return user

def update_user(user_id, updates):
    """Update user and invalidate cache"""
    # Update database
    cursor.execute("""
        UPDATE users SET username = %s, email = %s WHERE id = %s
    """, (updates['username'], updates['email'], user_id))
    conn.commit()

    # Invalidate cache
    cache_key = f'user:{user_id}'
    r.delete(cache_key)

    return get_user(user_id)  # Will cache fresh data
```

### Query Result Caching

```python
import hashlib

def cached_query(query, params, ttl=300):
    """
    Cache query results

    Args:
        query: SQL query string
        params: Query parameters
        ttl: Time to live in seconds

    Returns:
        Query results
    """
    # Create cache key from query and params
    key_data = f"{query}:{params}"
    cache_key = f"query:{hashlib.md5(key_data.encode()).hexdigest()}"

    # Try cache
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # Execute query
    cursor.execute(query, params)
    results = cursor.fetchall()

    # Cache results
    r.setex(cache_key, ttl, json.dumps(results))

    return results

# Usage
results = cached_query("""
    SELECT p.*, c.category_name
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE p.status = %s
    ORDER BY p.created_at DESC
    LIMIT 20
""", ('active',), ttl=300)
```

### Application-Level Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_category(category_id):
    """In-memory cache for frequently accessed, rarely changing data"""
    cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
    return cursor.fetchone()

# Clear cache when data changes
get_category.cache_clear()
```

## Connection Pooling

### Without Connection Pooling

```python
# ❌ Bad: New connection for each request
def handle_request():
    conn = psycopg2.connect(...)  # Expensive! (~10-50ms)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    conn.close()
    return results

# Problem:
# - Connection setup is expensive
# - Creates many connections to database
# - Doesn't scale to high traffic
```

### With Connection Pooling

```python
# ✅ Good: Connection pool
from psycopg2 import pool

# Create pool at application startup
db_pool = pool.SimpleConnectionPool(
    minconn=5,   # Minimum connections
    maxconn=20,  # Maximum connections
    host='localhost',
    database='myapp',
    user='postgres',
    password='password'
)

def handle_request():
    # Get connection from pool (fast!)
    conn = db_pool.getconn()

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        return results
    finally:
        # Return connection to pool
        db_pool.putconn(conn)

# Benefits:
# - Reuse connections (no setup overhead)
# - Limit concurrent connections
# - Better resource utilization
```

### SQLAlchemy Connection Pool

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:password@localhost/myapp',
    poolclass=QueuePool,
    pool_size=10,          # Connections to maintain
    max_overflow=20,       # Additional connections when needed
    pool_timeout=30,       # Wait time for connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Verify connections before using
)

# Use sessions
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

def handle_request():
    session = Session()
    try:
        users = session.query(User).all()
        return users
    finally:
        session.close()  # Returns connection to pool
```

## Monitoring and Profiling

### PostgreSQL: pg_stat_statements

```sql
-- Enable pg_stat_statements (postgresql.conf)
-- shared_preload_libraries = 'pg_stat_statements'

-- View slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time,
    stddev_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- Find queries needing indexes
SELECT
    query,
    calls,
    (total_time / calls) as avg_time
FROM pg_stat_statements
WHERE query LIKE '%Seq Scan%'
ORDER BY avg_time DESC;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

### MySQL: Performance Schema

```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- Queries slower than 1 second

-- View slow queries
SELECT *
FROM mysql.slow_log
ORDER BY query_time DESC
LIMIT 20;

-- Check table with missing indexes
SELECT
    OBJECT_SCHEMA,
    OBJECT_NAME,
    COUNT_READ as reads,
    COUNT_WRITE as writes
FROM performance_schema.table_io_waits_summary_by_table
WHERE OBJECT_SCHEMA NOT IN ('mysql', 'performance_schema')
ORDER BY COUNT_READ DESC;
```

### MongoDB: Profiling

```javascript
// Enable profiler
db.setProfilingLevel(2);  // Log all queries
// db.setProfilingLevel(1, { slowms: 100 });  // Log queries > 100ms

// View slow queries
db.system.profile.find().sort({ts: -1}).limit(10).pretty();

// Analyze query
db.users.find({email: 'john@example.com'}).explain('executionStats');

// Check index usage
db.users.aggregate([{$indexStats: {}}]);
```

### Python: Query Timing

```python
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_query_time(query_func):
    """Decorator to log query execution time"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = query_func(*args, **kwargs)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        if elapsed > 100:  # Log slow queries (>100ms)
            logger.warning(f"Slow query ({elapsed:.2f}ms): {query_func.__name__}")
        else:
            logger.info(f"Query executed ({elapsed:.2f}ms): {query_func.__name__}")

        return result
    return wrapper

@log_query_time
def get_users():
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()
```

## Real-World Optimization Examples

### Example 1: Slow Dashboard Query

**Problem:**
```sql
-- Original query: 5 seconds
SELECT
    u.username,
    COUNT(o.order_id) as order_count,
    SUM(o.total) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
GROUP BY u.id, u.username
ORDER BY total_spent DESC
LIMIT 100;
```

**Solution:**
```sql
-- Add indexes
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_total ON orders(total);

-- Optimized query: 50ms
-- Limit to recent orders for faster aggregation
SELECT
    u.username,
    COUNT(o.order_id) as order_count,
    SUM(o.total) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
    AND o.created_at > NOW() - INTERVAL '1 year'
WHERE u.status = 'active'
GROUP BY u.id, u.username
ORDER BY total_spent DESC
LIMIT 100;

-- Cache result for 5 minutes
-- Result: 100x faster!
```

### Example 2: Product Search

**Problem:**
```python
# Slow: Full-text search on large product table
def search_products(query):
    cursor.execute("""
        SELECT * FROM products
        WHERE name LIKE %s OR description LIKE %s
    """, (f'%{query}%', f'%{query}%'))
    return cursor.fetchall()
# 2-3 seconds for large catalog
```

**Solution:**
```python
# Use PostgreSQL full-text search with GIN index
cursor.execute("""
    CREATE INDEX idx_products_search ON products
    USING GIN (to_tsvector('english', name || ' ' || description))
""")

def search_products(query):
    cursor.execute("""
        SELECT * FROM products
        WHERE to_tsvector('english', name || ' ' || description)
            @@ plainto_tsquery('english', %s)
        ORDER BY ts_rank(
            to_tsvector('english', name || ' ' || description),
            plainto_tsquery('english', %s)
        ) DESC
        LIMIT 50
    """, (query, query))
    return cursor.fetchall()
# 50-100ms - 20-30x faster!

# Or use Elasticsearch for even better performance
```

### Example 3: Counting Large Tables

**Problem:**
```python
# Slow: COUNT(*) on large table
def get_user_count():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]
# 5-10 seconds for millions of rows
```

**Solution:**
```python
# Option 1: Use approximate count for PostgreSQL
def get_user_count_approximate():
    cursor.execute("""
        SELECT reltuples::bigint AS estimate
        FROM pg_class
        WHERE relname = 'users'
    """)
    return cursor.fetchone()[0]
# Instant! (May be slightly inaccurate)

# Option 2: Cache count and update incrementally
def increment_user_count():
    r.incr('user_count')

def decrement_user_count():
    r.decr('user_count')

def get_user_count():
    count = r.get('user_count')
    if count is None:
        # First time or cache expired
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        r.set('user_count', count)
    return int(count)
```

## Summary

Performance optimization checklist:

### Indexing
- ✅ Index foreign keys
- ✅ Index WHERE clause columns
- ✅ Index JOIN columns
- ✅ Use composite indexes strategically
- ✅ Don't over-index

### Queries
- ✅ Use EXPLAIN to analyze queries
- ✅ Select only needed columns
- ✅ Use LIMIT to cap results
- ✅ Avoid N+1 queries
- ✅ Use cursor-based pagination
- ✅ Batch operations when possible

### Caching
- ✅ Cache frequently accessed data
- ✅ Use appropriate TTL
- ✅ Invalidate cache on updates
- ✅ Cache at multiple layers

### Connections
- ✅ Use connection pooling
- ✅ Limit pool size appropriately
- ✅ Close connections properly
- ✅ Monitor connection usage

### Monitoring
- ✅ Enable query logging
- ✅ Track slow queries
- ✅ Monitor resource usage
- ✅ Set up alerts

## Next Steps

- [Security Best Practices](../10-security/README.md) - Secure your databases
- [Scaling Strategies](../11-scaling/README.md) - Scale to millions of users
- [Deployment Guide](../08-deployment/README.md) - Production deployment

---

[← Previous: Deployment](../08-deployment/README.md) | [Next: Security →](../10-security/README.md)
