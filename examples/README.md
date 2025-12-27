# Code Examples

This directory contains complete, runnable code examples demonstrating database connectivity and operations in various programming languages.

## Directory Structure

```
examples/
├── python/              # Python examples (PRIMARY FOCUS)
│   ├── postgresql_example.py
│   ├── mongodb_example.py
│   ├── redis_example.py
│   ├── mysql_example.py
│   └── requirements.txt
├── nodejs/              # Node.js examples
│   ├── postgresql_example.js
│   ├── mongodb_example.js
│   └── package.json
├── typescript/          # TypeScript examples
│   ├── postgresql_example.ts
│   ├── mongodb_example.ts
│   └── package.json
└── javascript/          # Plain JavaScript examples
    └── browser_api_example.js
```

## Python Examples (Primary Focus)

Python examples demonstrate best practices for database connectivity with comprehensive error handling, connection pooling, and production-ready patterns.

### Available Examples

1. **[postgresql_example.py](./python/postgresql_example.py)** - Complete PostgreSQL integration
   - Connection pooling with psycopg2
   - CRUD operations with Repository pattern
   - Transaction management
   - Bulk operations
   - Query optimization
   - Error handling

2. **[mongodb_example.py](./python/mongodb_example.py)** - MongoDB document database
   - pymongo integration
   - Document CRUD operations
   - Aggregation pipelines
   - Index management
   - Array and embedded document operations
   - Full-text search

3. **redis_example.py** - Redis caching and data structures
   - String, Hash, List, Set, Sorted Set operations
   - Caching patterns
   - Session management
   - Pub/Sub messaging
   - Expiration and TTL

4. **mysql_example.py** - MySQL connectivity
   - mysql-connector-python
   - Connection pooling
   - Transactions
   - Stored procedures

### Prerequisites for Python Examples

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r python/requirements.txt
```

### Running Python Examples

```bash
# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run PostgreSQL example
python python/postgresql_example.py

# Run MongoDB example
python python/mongodb_example.py

# Run Redis example
python python/redis_example.py
```

## Node.js Examples

Node.js examples demonstrate async/await patterns and modern JavaScript features.

### Prerequisites

```bash
cd nodejs
npm install
```

### Running Node.js Examples

```bash
# Set up environment
cp .env.example .env

# Run examples
node postgresql_example.js
node mongodb_example.js
```

## TypeScript Examples

TypeScript examples add type safety and demonstrate typed database access patterns.

### Prerequisites

```bash
cd typescript
npm install
```

### Running TypeScript Examples

```bash
# Compile TypeScript
npm run build

# Run compiled examples
node dist/postgresql_example.js
```

## Environment Variables

All examples use environment variables for configuration. Create a `.env` file:

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=tutorial_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=tutorial_db
MYSQL_USER=root
MYSQL_PASSWORD=your_password

# MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=tutorial_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

## Example Features

All examples demonstrate:

### Essential Patterns
- ✅ Connection pooling for production use
- ✅ Proper error handling and logging
- ✅ Transaction management
- ✅ Parameterized queries (SQL injection prevention)
- ✅ Resource cleanup (context managers, try/finally)
- ✅ Environment-based configuration

### Code Quality
- ✅ Clear documentation and comments
- ✅ Type hints (Python) / TypeScript types
- ✅ Consistent naming conventions
- ✅ Modular, reusable code
- ✅ Repository/DAO patterns

### Operations Covered
- ✅ CREATE: Inserting data (single and bulk)
- ✅ READ: Querying with filters, sorting, pagination
- ✅ UPDATE: Modifying existing data
- ✅ DELETE: Removing data safely
- ✅ SEARCH: Full-text and pattern matching
- ✅ AGGREGATE: Statistical queries and grouping

## Example Breakdown

### PostgreSQL Example Structure

```python
# 1. Configuration
DB_CONFIG = {...}  # From environment variables

# 2. Connection Pool
db_pool = pool.SimpleConnectionPool(...)  # Reusable connections

# 3. Context Manager
@contextmanager
def get_db_connection():
    # Automatic commit/rollback
    # Resource cleanup

# 4. Repository Pattern
class UserRepository:
    @staticmethod
    def create_user(...):
        # Insert with RETURNING clause

    @staticmethod
    def get_user(...):
        # Query with error handling

    @staticmethod
    def update_user(...):
        # Dynamic updates
        # Timestamp management

# 5. Demonstrations
demonstrate_crud_operations()
demonstrate_transactions()
demonstrate_bulk_operations()
```

### MongoDB Example Structure

```python
# 1. Client Connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# 2. Repository Pattern
class ProductRepository:
    collection = db['products']

    @classmethod
    def setup_indexes(cls):
        # Create performance indexes

    @classmethod
    def create_product(cls, data):
        # Document insertion

    @classmethod
    def aggregate_stats(cls):
        # Aggregation pipeline

# 3. Demonstrations
demonstrate_crud_operations()
demonstrate_aggregations()
demonstrate_array_operations()
```

## Best Practices Demonstrated

### Security
```python
# ✅ Good: Parameterized query
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# ❌ Bad: String formatting (SQL injection risk)
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### Connection Management
```python
# ✅ Good: Connection pooling
db_pool = pool.SimpleConnectionPool(1, 10, **config)
conn = db_pool.getconn()

# ❌ Bad: New connection each time
conn = psycopg2.connect(**config)  # Expensive!
```

### Error Handling
```python
# ✅ Good: Specific exception handling
try:
    cursor.execute(query)
except psycopg2.IntegrityError as e:
    logger.error(f"Duplicate entry: {e}")
    raise
except psycopg2.OperationalError as e:
    logger.error(f"Connection error: {e}")
    retry_connection()
```

### Transaction Management
```python
# ✅ Good: Context manager with auto-rollback
with get_db_connection() as conn:
    cursor.execute(...)  # Auto-commit on success
    # Auto-rollback on exception

# ❌ Bad: Manual commit/rollback
conn.commit()  # Easy to forget!
```

## Docker Setup for Testing

Quick setup using Docker:

```bash
# PostgreSQL
docker run -d \
  --name postgres-tutorial \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=tutorial_db \
  -p 5432:5432 \
  postgres:15

# MongoDB
docker run -d \
  --name mongo-tutorial \
  -p 27017:27017 \
  mongo:7

# Redis
docker run -d \
  --name redis-tutorial \
  -p 6379:6379 \
  redis:7

# MySQL
docker run -d \
  --name mysql-tutorial \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=tutorial_db \
  -p 3306:3306 \
  mysql:8
```

## Troubleshooting

### Connection Issues

**PostgreSQL:**
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U postgres -d tutorial_db
```

**MongoDB:**
```bash
# Check MongoDB status
mongosh --eval "db.adminCommand('ping')"
```

**Redis:**
```bash
# Test Redis connection
redis-cli ping
```

### Common Errors

**Error: "role does not exist"**
```bash
# Create PostgreSQL user
createuser -s postgres
```

**Error: "database does not exist"**
```bash
# Create database
createdb tutorial_db
```

**Error: "connection refused"**
```bash
# Check if database is running
docker ps  # If using Docker
```

## Performance Tips

### PostgreSQL
- Use connection pooling (demonstrated in examples)
- Create indexes on frequently queried columns
- Use EXPLAIN ANALYZE to check query plans
- Batch inserts for bulk operations

### MongoDB
- Create indexes for query patterns
- Use projection to limit returned fields
- Leverage aggregation pipeline for complex queries
- Use bulk operations for multiple writes

### Redis
- Use pipelining for multiple operations
- Set appropriate TTLs to manage memory
- Use Redis data structures appropriately
- Monitor memory usage

## Learning Path

1. **Start with Python examples** (most comprehensive)
2. **Run each example** and observe output
3. **Modify examples** to experiment
4. **Read the code comments** for explanations
5. **Try the variations** suggested in comments
6. **Check other language examples** for comparison

## Related Resources

- [Python Backend Connectivity Guide](../05-backend-connectivity/python/README.md)
- [Beginner Exercises](../exercises/beginner/README.md)
- [Intermediate Exercises](../exercises/intermediate/README.md)
- [Setup and Configuration](../04-setup-and-configuration/README.md)

## Contributing Examples

To contribute new examples:
1. Follow existing code structure
2. Include comprehensive comments
3. Add error handling
4. Demonstrate best practices
5. Include setup instructions
6. Test thoroughly

## Questions or Issues?

- Check the [main README](../README.md)
- Review [troubleshooting guide](../04-setup-and-configuration/README.md)
- Consult specific database sections

---

**Ready to start?** Pick an example and run it!

**Want to learn more?** Check out the [complete tutorial](../README.md)
