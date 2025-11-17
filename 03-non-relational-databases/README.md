# Part 3: Non-Relational Databases (NoSQL)

## Overview

Non-relational databases, commonly known as NoSQL (Not Only SQL), provide flexible data models and horizontal scalability. This section covers the major NoSQL database types with practical examples and use cases.

## What You'll Learn

- NoSQL fundamentals and when to use them
- Document databases: MongoDB
- Wide-column stores: Cassandra
- Key-value stores: Redis
- AWS DynamoDB (key-value/document hybrid)
- Data modeling for NoSQL
- CAP theorem in practice
- Polyglot persistence strategies

## NoSQL vs SQL: When to Choose NoSQL

### Choose NoSQL When:
- **Schema flexibility** is required (evolving data models)
- **Horizontal scalability** is essential (millions of users)
- **High write throughput** is needed (logging, time-series)
- **Denormalized data** is acceptable
- **Eventual consistency** is sufficient
- **Specific data structures** fit your use case (graphs, documents, key-value)

### Stick with SQL When:
- **ACID transactions** are mandatory
- **Complex queries** with joins are frequent
- **Data integrity** is critical (financial systems)
- **Strong consistency** is required
- **Mature tooling** is needed
- **Relationship complexity** is high

## NoSQL Categories

```
NoSQL Databases
│
├── Document Stores
│   ├── MongoDB (most popular)
│   ├── CouchDB
│   └── Amazon DocumentDB
│
├── Key-Value Stores
│   ├── Redis (in-memory)
│   ├── Amazon DynamoDB
│   └── Riak
│
├── Wide-Column Stores
│   ├── Apache Cassandra
│   ├── HBase
│   └── Google Bigtable
│
├── Graph Databases
│   ├── Neo4j
│   ├── Amazon Neptune
│   └── ArangoDB (multi-model)
│
└── Time-Series Databases
    ├── InfluxDB
    ├── TimescaleDB
    └── OpenTSDB
```

## CAP Theorem in Practice

The CAP theorem states you can only guarantee two of three properties in a distributed system:

### Consistency (C)
All nodes see the same data at the same time.

### Availability (A)
Every request receives a response (success or failure).

### Partition Tolerance (P)
System continues operating despite network partitions.

### NoSQL Databases and CAP

| Database | CAP Category | Trade-off Choice |
|----------|-------------|------------------|
| **MongoDB** | CP (tunable) | Can configure for AP or CP |
| **Cassandra** | AP | Prioritizes availability |
| **Redis** | CP | Strong consistency, may reject writes |
| **DynamoDB** | AP | Eventually consistent (tunable) |
| **HBase** | CP | Strong consistency |

### Real-World Example

```python
# MongoDB: Tunable consistency
# Write Concern: Controls write acknowledgment
collection.insert_one(
    document,
    write_concern=WriteConcern(w='majority')  # Wait for majority
)

# Read Concern: Controls read isolation
collection.find_one(
    filter,
    read_concern=ReadConcern('majority')  # Read majority-committed data
)

# Cassandra: Eventual consistency with tunable levels
# Consistency Level: Controls read/write behavior
session.execute(
    query,
    consistency_level=ConsistencyLevel.QUORUM  # Read from majority
)
```

## Data Modeling Differences

### Relational (Normalized)
```
Users Table:
┌────────┬──────────┬─────────────────────┐
│ user_id│ username │ email               │
├────────┼──────────┼─────────────────────┤
│ 1      │ john     │ john@example.com    │
└────────┴──────────┴─────────────────────┘

Orders Table:
┌──────────┬─────────┬────────────┬────────┐
│ order_id │ user_id │ order_date │ total  │
├──────────┼─────────┼────────────┼────────┤
│ 101      │ 1       │ 2024-01-15 │ 150.00 │
└──────────┴─────────┴────────────┴────────┘

Order_Items Table:
┌─────────┬──────────┬────────────┬──────────┐
│ item_id │ order_id │ product_id │ quantity │
├─────────┼──────────┼────────────┼──────────┤
│ 1       │ 101      │ 500        │ 2        │
└─────────┴──────────┴────────────┴──────────┘
```

### Document Database (Denormalized)
```javascript
// MongoDB: Embedded document approach
{
  _id: ObjectId("..."),
  username: "john",
  email: "john@example.com",
  orders: [
    {
      order_id: 101,
      order_date: ISODate("2024-01-15"),
      total: 150.00,
      items: [
        {
          product_id: 500,
          product_name: "Laptop",
          quantity: 2,
          price: 75.00
        }
      ]
    }
  ]
}
```

**Trade-offs:**
- ✅ Single query retrieves all user data
- ✅ No joins needed
- ❌ Data duplication
- ❌ Updates require updating multiple documents

## Section Contents

### [Introduction to NoSQL](./introduction.md)
Comprehensive introduction to NoSQL concepts, history, and use cases.

### [MongoDB - Document Database](./mongodb/README.md)
**Most popular document database**

**What you'll learn:**
- Document data model and BSON format
- CRUD operations and queries
- Aggregation framework
- Indexing strategies
- Replication and sharding
- Python integration (pymongo)
- Schema design patterns
- Transactions (MongoDB 4.0+)

**Use cases:**
- Content management systems
- User profiles and catalogs
- Real-time analytics
- Mobile applications
- Internet of Things (IoT)

### [Apache Cassandra - Wide-Column Store](./cassandra/README.md)
**Designed for high availability and linear scalability**

**What you'll learn:**
- Column family data model
- CQL (Cassandra Query Language)
- Partition keys and clustering columns
- Data modeling for queries
- Replication strategies
- Consistency levels
- Python integration (cassandra-driver)
- Time-series data patterns

**Use cases:**
- Time-series data (sensor data, logs)
- High-volume writes (event logging)
- Messaging systems
- Product catalogs
- Recommendation engines

### [Redis - Key-Value Store](./redis/README.md)
**In-memory data structure store**

**What you'll learn:**
- Data structures (strings, hashes, lists, sets, sorted sets)
- Pub/Sub messaging
- Caching strategies
- Session management
- Rate limiting
- Python integration (redis-py)
- Persistence options (RDB, AOF)
- Redis Cluster for scaling

**Use cases:**
- Caching layer
- Session storage
- Real-time analytics
- Leaderboards
- Message queues
- Rate limiting

### [Amazon DynamoDB](./dynamodb/README.md)
**Fully managed key-value and document database**

**What you'll learn:**
- DynamoDB data model
- Primary keys and indexes
- Provisioned vs on-demand capacity
- DynamoDB Streams
- Global tables (multi-region)
- Python integration (boto3)
- Single-table design patterns
- Cost optimization

**Use cases:**
- Serverless applications
- Gaming leaderboards
- Mobile backends
- IoT applications
- E-commerce carts

### [When to Use NoSQL](./when-to-use-nosql.md)
Decision framework for choosing NoSQL databases, migration strategies, and polyglot persistence.

## Quick Comparison

| Feature | MongoDB | Cassandra | Redis | DynamoDB |
|---------|---------|-----------|-------|----------|
| **Type** | Document | Wide-Column | Key-Value | Hybrid |
| **Query Language** | MongoDB Query | CQL | Commands | API |
| **Consistency** | Tunable | Tunable | Strong | Eventual |
| **Scalability** | Horizontal | Horizontal | Horizontal | Automatic |
| **Best For** | Flexible docs | Time-series | Caching | Serverless |
| **ACID** | Yes (4.0+) | No | Partial | Limited |
| **Learning Curve** | Medium | Steep | Easy | Medium |
| **Hosting** | Self/Atlas | Self-hosted | Self/Cloud | AWS Only |

## Common NoSQL Patterns

### 1. Denormalization

**Relational approach (normalized):**
```sql
-- Multiple queries needed
SELECT * FROM users WHERE id = 1;
SELECT * FROM orders WHERE user_id = 1;
SELECT * FROM order_items WHERE order_id IN (...);
```

**NoSQL approach (denormalized):**
```javascript
// Single query retrieves everything
db.users.findOne({ _id: 1 })
// Returns user with embedded orders and items
```

### 2. Eventual Consistency

```python
# Write to multiple nodes
# Eventually all nodes will have the same data

# Write operation
dynamodb.put_item(TableName='users', Item={'id': '1', 'name': 'John'})

# Read immediately after write might return old data
# But eventually (milliseconds to seconds) will be consistent
item = dynamodb.get_item(TableName='users', Key={'id': '1'})
```

### 3. Time-to-Live (TTL)

```python
# Redis: Automatic expiration
redis.setex('session:abc123', 3600, session_data)  # Expires in 1 hour

# MongoDB: TTL index
db.sessions.create_index(
    'createdAt',
    expireAfterSeconds=3600  # Documents expire 1 hour after creation
)

# DynamoDB: TTL attribute
dynamodb.put_item(
    TableName='sessions',
    Item={
        'session_id': 'abc123',
        'data': session_data,
        'ttl': int(time.time()) + 3600  # Unix timestamp for expiration
    }
)
```

### 4. Sharding/Partitioning

```python
# Cassandra: Partition key determines data distribution
CREATE TABLE sensor_data (
    sensor_id UUID,      -- Partition key
    timestamp TIMESTAMP, -- Clustering column
    temperature FLOAT,
    PRIMARY KEY ((sensor_id), timestamp)
);
# Data for each sensor_id goes to specific nodes

# MongoDB: Shard key distributes data
sh.shardCollection('mydb.users', { user_id: 'hashed' })
# Users distributed across shards based on hashed user_id
```

## Migration from SQL to NoSQL

### Planning Your Migration

**Step 1: Identify Use Cases**
```
Audit your application:
✓ Which tables have flexible schemas?
✓ Which queries don't need joins?
✓ Which data is accessed together?
✓ Which parts need high write throughput?
✓ Which parts can tolerate eventual consistency?
```

**Step 2: Choose the Right NoSQL Database**
```
Document Store (MongoDB):
- If you have nested/hierarchical data
- If schema changes frequently
- If you need flexible queries

Key-Value (Redis/DynamoDB):
- If access pattern is simple lookups
- If you need high performance
- If data is ephemeral (Redis) or event-driven (DynamoDB)

Wide-Column (Cassandra):
- If you have time-series data
- If you need massive write throughput
- If you query by time ranges
```

**Step 3: Redesign Data Model**
```sql
-- Relational: Normalized
Users, Orders, OrderItems (3 tables, joins required)

-- NoSQL: Denormalized
{
  user: {...},
  orders: [{items: [...]}]  // Embedded in single document
}
```

**Step 4: Phased Migration**
```
Phase 1: Dual-Write
  - Write to both SQL and NoSQL
  - Read from SQL (existing app)
  - Verify data consistency

Phase 2: Dual-Read
  - Continue dual-write
  - Read from NoSQL
  - Fall back to SQL if needed

Phase 3: Cutover
  - NoSQL is primary
  - Stop writing to SQL
  - Archive SQL data

Phase 4: Optimize
  - Remove SQL database
  - Optimize NoSQL queries
  - Add indexes as needed
```

### Example: E-Commerce Product Catalog

**Before (PostgreSQL):**
```sql
-- Products table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(50),
    price DECIMAL(10,2)
);

-- Product attributes (EAV pattern - slow queries)
CREATE TABLE product_attributes (
    attribute_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    attribute_name VARCHAR(50),
    attribute_value TEXT
);

-- Query requires join
SELECT p.*, pa.attribute_name, pa.attribute_value
FROM products p
LEFT JOIN product_attributes pa ON p.product_id = pa.product_id
WHERE p.product_id = 123;
```

**After (MongoDB):**
```javascript
// Single document with flexible schema
{
  _id: ObjectId("..."),
  name: "Wireless Headphones",
  category: "Electronics",
  price: 79.99,
  attributes: {
    // Flexible attributes - no joins needed
    bluetooth: "5.0",
    battery_life: "30 hours",
    noise_cancellation: true,
    colors: ["black", "white", "blue"]
  },
  specifications: {
    weight: "250g",
    dimensions: {
      width: 180,
      height: 200,
      depth: 80,
      unit: "mm"
    }
  },
  reviews: [
    {rating: 5, comment: "Great product!", date: ISODate("2024-01-15")},
    {rating: 4, comment: "Good value", date: ISODate("2024-01-20")}
  ]
}

// Single query retrieves everything
db.products.findOne({_id: ObjectId("...")})
```

**Benefits of Migration:**
- ✅ Single query instead of joins
- ✅ Schema flexibility for new product types
- ✅ Easier to add new attributes
- ✅ Better performance for product pages
- ✅ Nested data (reviews, specs) naturally modeled

## Polyglot Persistence

Using multiple database types in one application:

```
Application Architecture:
┌─────────────────────────────────────────────┐
│           Application Layer                 │
└─────────────┬───────────────────────────────┘
              │
    ┌─────────┼──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌──▼───┐  ┌───▼────┐ ┌──▼─────┐
│ PostgreSQL│ MongoDB│ │  Redis │ │ ElasticSearch│
│ (Users,   │ (Logs, │ │(Cache) │ │ (Search)     │
│  Orders)  │ Events)│ │        │ │              │
└───────────┘ └──────┘ └────────┘ └──────────────┘

Use case breakdown:
- PostgreSQL: User accounts, orders (ACID required)
- MongoDB: Product catalog, user activity logs
- Redis: Session storage, caching
- Elasticsearch: Product search
```

### Example Implementation

```python
class OrderService:
    """Service using multiple databases"""

    def __init__(self):
        self.postgres = PostgresConnection()  # Orders, transactions
        self.mongo = MongoConnection()        # Order events, logs
        self.redis = RedisConnection()        # Cache
        self.es = ElasticsearchConnection()   # Search

    def create_order(self, user_id, items):
        # PostgreSQL: Create order (ACID transaction)
        with self.postgres.transaction():
            order = self.postgres.execute("""
                INSERT INTO orders (user_id, total, status)
                VALUES (%s, %s, %s)
                RETURNING order_id
            """, (user_id, total, 'pending'))

            for item in items:
                self.postgres.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                """, (order['order_id'], item['product_id'], item['quantity']))

        # MongoDB: Log order event
        self.mongo.orders_log.insert_one({
            'order_id': order['order_id'],
            'user_id': user_id,
            'event': 'order_created',
            'timestamp': datetime.utcnow(),
            'items': items
        })

        # Redis: Invalidate cache
        self.redis.delete(f'user:{user_id}:orders')

        return order

    def get_order(self, order_id):
        # Redis: Try cache first
        cache_key = f'order:{order_id}'
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # PostgreSQL: Fetch from database
        order = self.postgres.fetch_one("""
            SELECT * FROM orders WHERE order_id = %s
        """, (order_id,))

        # Redis: Cache result
        self.redis.setex(cache_key, 300, json.dumps(order))

        return order
```

## NoSQL Best Practices

### 1. Design for Your Queries
```javascript
// ❌ Bad: Design first, query later
{
  _id: ObjectId("..."),
  user_id: 123,
  // ... fields
}
// Later realize you need to query by email - slow without index!

// ✅ Good: Know your queries, design accordingly
{
  _id: ObjectId("..."),
  user_id: 123,
  email: "john@example.com",  // Will be queried
  // ... other fields
}
// Create index on email immediately
db.users.createIndex({email: 1})
```

### 2. Avoid Large Documents
```javascript
// ❌ Bad: Unbounded array growth
{
  user_id: 123,
  posts: [...]  // Could grow to millions - document size limit!
}

// ✅ Good: Separate collection for large datasets
{
  user_id: 123,
  post_count: 1500,
  recent_posts: [...]  // Only last 10 posts
}
// Separate posts collection
db.posts.find({user_id: 123})
```

### 3. Use Appropriate Indexes
```python
# MongoDB: Compound index for common queries
db.products.create_index([
    ('category', 1),
    ('price', -1)
])

# Query uses index
db.products.find({'category': 'Electronics'}).sort({'price': -1})
```

### 4. Monitor Performance
```python
# MongoDB: Explain query
db.products.find({'category': 'Electronics'}).explain('executionStats')

# Cassandra: Tracing
session.execute(query, trace=True)
print(session.get_query_trace())

# Redis: Slowlog
redis.slowlog_get(10)  # Get 10 slowest queries
```

## Learning Path

### Beginner
1. Start with [Introduction to NoSQL](./introduction.md)
2. Learn [MongoDB basics](./mongodb/README.md)
3. Practice with [MongoDB examples](../../examples/python/mongodb_example.py)
4. Complete [beginner exercises](../../exercises/beginner/README.md)

### Intermediate
1. Explore [Redis for caching](./redis/README.md)
2. Learn [Cassandra for time-series](./cassandra/README.md)
3. Study [DynamoDB patterns](./dynamodb/README.md)
4. Practice [intermediate exercises](../../exercises/intermediate/README.md)

### Advanced
1. Implement [polyglot persistence](./when-to-use-nosql.md)
2. Design [sharding strategies](../11-scaling/sharding.md)
3. Optimize [query performance](../09-performance/README.md)
4. Build [production systems](../08-deployment/README.md)

## Summary

NoSQL databases excel at:
- **Flexibility**: Schema-less or flexible schemas
- **Scalability**: Horizontal scaling for massive data
- **Performance**: Optimized for specific access patterns
- **Availability**: Designed for distributed systems

Choose NoSQL when:
- Schema changes frequently
- Need horizontal scalability
- Specific data models fit your use case
- Eventual consistency is acceptable
- High write throughput is required

## Next Steps

1. [Introduction to NoSQL](./introduction.md) - Deep dive into concepts
2. [MongoDB Guide](./mongodb/README.md) - Most popular document database
3. [Redis Guide](./redis/README.md) - High-performance caching
4. [When to Use NoSQL](./when-to-use-nosql.md) - Decision framework

---

[← Previous: Relational Databases](../02-relational-databases/README.md) | [Next: MongoDB →](./mongodb/README.md)
