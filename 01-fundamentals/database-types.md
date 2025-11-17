# Database Types and Categories

## Introduction

Understanding different database types is crucial for selecting the right tool for your specific use case. Each database type has been designed to excel at particular workloads and data patterns.

## Database Classification

```
Databases
├── Relational (SQL)
│   ├── Traditional RDBMS (PostgreSQL, MySQL, Oracle)
│   └── NewSQL (CockroachDB, Google Spanner)
├── Non-Relational (NoSQL)
│   ├── Document Stores (MongoDB, CouchDB)
│   ├── Key-Value Stores (Redis, DynamoDB)
│   ├── Wide-Column Stores (Cassandra, HBase)
│   ├── Graph Databases (Neo4j, Neptune)
│   └── Time-Series (InfluxDB, TimescaleDB)
└── Specialized
    ├── In-Memory (Redis, Memcached)
    ├── Search Engines (Elasticsearch, Solr)
    └── Vector Databases (Pinecone, Weaviate)
```

## 1. Relational Databases (SQL)

### Overview
Relational databases store data in tables with predefined schemas. They use SQL (Structured Query Language) and emphasize ACID compliance.

### Characteristics
- **Structured data** organized in tables (rows and columns)
- **Schema-based** - structure defined before data insertion
- **ACID compliant** - strong consistency guarantees
- **Relationships** via foreign keys
- **Powerful querying** with joins, aggregations, subqueries

### When to Use
- Structured data with clear relationships
- Need for complex queries and transactions
- Strong consistency requirements
- Financial systems, ERP, CRM applications
- Data integrity is critical

### Popular Relational Databases

#### PostgreSQL
```sql
-- Example: Creating a relational schema
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    dept_id INTEGER REFERENCES departments(dept_id),
    salary DECIMAL(10, 2),
    hire_date DATE
);

-- Complex query with joins
SELECT
    d.dept_name,
    COUNT(e.emp_id) as employee_count,
    AVG(e.salary) as avg_salary
FROM departments d
LEFT JOIN employees e ON d.dept_id = e.dept_id
GROUP BY d.dept_name;
```

**Strengths:**
- Advanced features (JSON support, full-text search, PostGIS)
- Strong compliance with SQL standards
- Extensible with custom functions and types
- Excellent for complex queries

#### MySQL
```sql
-- Example: Transaction with stored procedure
DELIMITER //
CREATE PROCEDURE transfer_funds(
    IN from_account INT,
    IN to_account INT,
    IN amount DECIMAL(10,2)
)
BEGIN
    START TRANSACTION;

    UPDATE accounts SET balance = balance - amount
    WHERE account_id = from_account;

    UPDATE accounts SET balance = balance + amount
    WHERE account_id = to_account;

    COMMIT;
END //
DELIMITER ;
```

**Strengths:**
- Fast read performance
- Wide adoption and community
- Good for web applications
- Multiple storage engines (InnoDB, MyISAM)

#### Microsoft SQL Server
```sql
-- Example: Window functions and CTEs
WITH RankedSales AS (
    SELECT
        salesperson_id,
        sale_date,
        amount,
        ROW_NUMBER() OVER (
            PARTITION BY salesperson_id
            ORDER BY amount DESC
        ) as rank
    FROM sales
)
SELECT * FROM RankedSales WHERE rank <= 3;
```

**Strengths:**
- Enterprise features
- Excellent integration with Microsoft ecosystem
- Advanced analytics and reporting
- High availability features

#### Oracle Database
```sql
-- Example: Advanced partitioning
CREATE TABLE sales (
    sale_id NUMBER,
    sale_date DATE,
    amount NUMBER
)
PARTITION BY RANGE (sale_date) (
    PARTITION sales_q1 VALUES LESS THAN (TO_DATE('2024-04-01', 'YYYY-MM-DD')),
    PARTITION sales_q2 VALUES LESS THAN (TO_DATE('2024-07-01', 'YYYY-MM-DD')),
    PARTITION sales_q3 VALUES LESS THAN (TO_DATE('2024-10-01', 'YYYY-MM-DD')),
    PARTITION sales_q4 VALUES LESS THAN (TO_DATE('2025-01-01', 'YYYY-MM-DD'))
);
```

**Strengths:**
- Most mature enterprise RDBMS
- Highest performance and scalability
- Advanced security features
- Multi-tenancy support

### Pros and Cons

**Pros:**
- Mature technology with decades of optimization
- Strong data consistency
- Powerful query capabilities
- ACID compliance
- Well-understood and documented

**Cons:**
- Vertical scaling can be expensive
- Schema changes can be complex
- May not scale horizontally as easily as NoSQL
- Can be overkill for simple data structures

## 2. Document Databases

### Overview
Document databases store data in flexible, JSON-like documents. Each document can have a different structure.

### Characteristics
- **Schema-flexible** - documents can vary in structure
- **Nested data** - documents can contain arrays and sub-documents
- **Denormalization** encouraged for performance
- **Query by document fields**

### When to Use
- Semi-structured or rapidly changing data
- Content management systems
- User profiles with varying attributes
- Catalog systems
- Mobile applications

### MongoDB Example

```javascript
// Example: Document structure
{
    "_id": ObjectId("507f1f77bcf86cd799439011"),
    "username": "johndoe",
    "email": "john@example.com",
    "profile": {
        "firstName": "John",
        "lastName": "Doe",
        "age": 30,
        "address": {
            "street": "123 Main St",
            "city": "Boston",
            "country": "USA"
        }
    },
    "orders": [
        {
            "orderId": "ORD001",
            "date": ISODate("2024-01-15"),
            "total": 150.00,
            "items": [
                {"product": "Laptop", "quantity": 1, "price": 150.00}
            ]
        }
    ],
    "tags": ["premium", "verified"],
    "createdAt": ISODate("2024-01-01")
}

// Querying documents
db.users.find({
    "profile.age": {$gte: 18},
    "tags": "verified"
}).sort({"createdAt": -1}).limit(10);

// Aggregation pipeline
db.users.aggregate([
    {$match: {"tags": "premium"}},
    {$unwind: "$orders"},
    {$group: {
        _id: "$_id",
        totalSpent: {$sum: "$orders.total"}
    }},
    {$sort: {totalSpent: -1}}
]);
```

### Pros and Cons

**Pros:**
- Flexible schema - easy to evolve
- Natural mapping to application objects
- Horizontal scalability
- Fast for read-heavy workloads
- Good for hierarchical data

**Cons:**
- Potential data duplication
- Complex joins are difficult
- Consistency can be eventual
- Query optimization requires understanding

## 3. Key-Value Databases

### Overview
Simplest NoSQL model - stores data as key-value pairs. Optimized for fast lookups by key.

### Characteristics
- **Simple data model** - unique key maps to a value
- **High performance** - O(1) lookups
- **Horizontally scalable**
- **Often in-memory** for speed

### When to Use
- Caching layers
- Session storage
- Real-time analytics
- Shopping carts
- User preferences
- Leaderboards

### Redis Example

```python
import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Simple key-value operations
r.set('user:1000:name', 'John Doe')
name = r.get('user:1000:name')  # b'John Doe'

# Store complex data as JSON
import json
user_data = {
    'username': 'johndoe',
    'email': 'john@example.com',
    'score': 1500
}
r.set('user:1000', json.dumps(user_data))

# Hash operations (field-value pairs)
r.hset('user:1001', mapping={
    'username': 'janedoe',
    'email': 'jane@example.com',
    'score': '2000'
})
score = r.hget('user:1001', 'score')

# Lists (for queues, activity feeds)
r.lpush('notifications:user:1000', 'New message from Jane')
r.lpush('notifications:user:1000', 'Order shipped')
notifications = r.lrange('notifications:user:1000', 0, 9)  # Get 10 most recent

# Sets (for unique collections)
r.sadd('user:1000:interests', 'python', 'databases', 'cloud')
interests = r.smembers('user:1000:interests')

# Sorted sets (leaderboards)
r.zadd('game:leaderboard', {
    'player1': 1500,
    'player2': 2000,
    'player3': 1800
})
top_players = r.zrevrange('game:leaderboard', 0, 2, withscores=True)

# Time-to-live (TTL)
r.setex('session:abc123', 3600, 'session_data')  # Expires in 1 hour
```

### Amazon DynamoDB Example

```python
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Users')

# Put item
table.put_item(
    Item={
        'userId': '12345',
        'username': 'johndoe',
        'email': 'john@example.com',
        'registrationDate': '2024-01-01',
        'preferences': {
            'theme': 'dark',
            'notifications': True
        }
    }
)

# Get item
response = table.get_item(Key={'userId': '12345'})
user = response['Item']

# Query with conditions
response = table.query(
    IndexName='EmailIndex',
    KeyConditionExpression='email = :email',
    ExpressionAttributeValues={':email': 'john@example.com'}
)
```

### Pros and Cons

**Pros:**
- Extremely fast lookups
- Simple to understand and use
- Highly scalable
- Excellent for caching
- Low latency

**Cons:**
- Limited query capabilities
- No complex queries or joins
- Difficult to model relationships
- Range queries require sorted sets or secondary structures

## 4. Wide-Column Databases

### Overview
Store data in column families, allowing for flexible schemas and efficient column-based queries.

### Characteristics
- **Column-oriented storage** - data stored by columns
- **Flexible schemas** - columns can vary per row
- **Distributed architecture** - designed for horizontal scaling
- **High write throughput**

### When to Use
- Time-series data
- Event logging
- IoT sensor data
- Analytics workloads
- Large-scale distributed systems

### Cassandra Example

```sql
-- Create keyspace (database)
CREATE KEYSPACE user_activity
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 3
};

-- Create table (column family)
CREATE TABLE user_activity.events (
    user_id UUID,
    event_time TIMESTAMP,
    event_type TEXT,
    event_data MAP<TEXT, TEXT>,
    PRIMARY KEY ((user_id), event_time)
) WITH CLUSTERING ORDER BY (event_time DESC);

-- Insert data
INSERT INTO user_activity.events (
    user_id, event_time, event_type, event_data
) VALUES (
    uuid(),
    toTimestamp(now()),
    'page_view',
    {'page': '/products', 'duration': '45s'}
);

-- Query by partition key
SELECT * FROM user_activity.events
WHERE user_id = 123e4567-e89b-12d3-a456-426614174000
AND event_time >= '2024-01-01'
LIMIT 100;
```

```python
# Python example with Cassandra
from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('user_activity')

# Prepared statements for efficiency
prepared = session.prepare("""
    INSERT INTO events (user_id, event_time, event_type, event_data)
    VALUES (?, ?, ?, ?)
""")

# Execute batch operations
from cassandra.query import BatchStatement
batch = BatchStatement()
for event in events:
    batch.add(prepared, (event.user_id, event.timestamp, event.type, event.data))
session.execute(batch)
```

### Pros and Cons

**Pros:**
- Excellent write performance
- Linear scalability
- No single point of failure
- Good for time-series data
- Handles high volume well

**Cons:**
- Limited query flexibility
- Eventual consistency
- Requires careful data modeling
- Learning curve for query patterns

## 5. Graph Databases

### Overview
Optimized for storing and querying relationships between entities using nodes, edges, and properties.

### Characteristics
- **Nodes** - entities (users, products, locations)
- **Edges** - relationships between nodes
- **Properties** - attributes on nodes and edges
- **Efficient traversals** - follow relationships quickly

### When to Use
- Social networks
- Recommendation engines
- Fraud detection
- Knowledge graphs
- Network and IT operations
- Route optimization

### Neo4j Example

```cypher
// Create nodes
CREATE (john:Person {name: 'John Doe', age: 30})
CREATE (jane:Person {name: 'Jane Smith', age: 28})
CREATE (python:Technology {name: 'Python', category: 'Programming Language'})
CREATE (aws:Technology {name: 'AWS', category: 'Cloud Platform'})

// Create relationships
CREATE (john)-[:KNOWS {since: 2020}]->(jane)
CREATE (john)-[:SKILLED_IN {level: 'Expert'}]->(python)
CREATE (john)-[:SKILLED_IN {level: 'Intermediate'}]->(aws)
CREATE (jane)-[:SKILLED_IN {level: 'Advanced'}]->(python)

// Query: Find John's friends who know Python
MATCH (john:Person {name: 'John Doe'})-[:KNOWS]->(friend)
      -[:SKILLED_IN]->(tech:Technology {name: 'Python'})
RETURN friend.name, tech.name

// Query: Recommendation - find technologies that John's friends know
MATCH (john:Person {name: 'John Doe'})-[:KNOWS]->(friend)
      -[:SKILLED_IN]->(tech:Technology)
WHERE NOT (john)-[:SKILLED_IN]->(tech)
RETURN tech.name, COUNT(friend) as friend_count
ORDER BY friend_count DESC

// Query: Find shortest path
MATCH path = shortestPath(
    (john:Person {name: 'John Doe'})-[*]-(company:Company {name: 'TechCorp'})
)
RETURN path
```

```python
# Python with Neo4j
from neo4j import GraphDatabase

class GraphDB:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def find_connections(self, person_name, max_depth=3):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Person {name: $name})-[:KNOWS*1..{depth}]-(connection)
                RETURN DISTINCT connection.name as name
            """, name=person_name, depth=max_depth)
            return [record["name"] for record in result]

    def recommend_friends(self, person_name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Person {name: $name})-[:KNOWS]-(friend)-[:KNOWS]-(recommendation)
                WHERE NOT (p)-[:KNOWS]-(recommendation) AND p <> recommendation
                RETURN recommendation.name as name, COUNT(*) as mutual_friends
                ORDER BY mutual_friends DESC
                LIMIT 10
            """, name=person_name)
            return [(r["name"], r["mutual_friends"]) for r in result]
```

### Pros and Cons

**Pros:**
- Natural representation of relationships
- Efficient traversals
- Flexible schema
- Pattern matching queries
- Real-time insights

**Cons:**
- Not suitable for simple lookups
- Scaling can be complex
- Query performance depends on graph size
- Specialized use cases

## 6. Time-Series Databases

### Overview
Optimized for time-stamped or time-series data, with features for efficient storage and querying of temporal data.

### Characteristics
- **Time-based indexing**
- **Data retention policies**
- **Downsampling and aggregation**
- **Continuous queries**

### When to Use
- IoT sensor data
- Application monitoring
- Financial market data
- Server metrics
- DevOps monitoring

### InfluxDB Example

```sql
-- InfluxDB Line Protocol
-- measurement,tag=value field=value timestamp

-- Writing data
cpu,host=server1,region=us-east value=64.5 1622548800000000000
memory,host=server1,region=us-east value=80.2 1622548800000000000

-- Queries
SELECT mean("value") FROM "cpu"
WHERE time > now() - 1h
GROUP BY time(5m), "host"

-- Downsampling with continuous queries
CREATE CONTINUOUS QUERY "cpu_mean_5m" ON "mydb"
BEGIN
    SELECT mean("value") INTO "cpu_mean" FROM "cpu"
    GROUP BY time(5m), *
END
```

```python
# Python with InfluxDB
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

client = InfluxDBClient(url="http://localhost:8086", token="my-token", org="my-org")
write_api = client.write_api(write_options=SYNCHRONOUS)

# Write data points
point = Point("temperature") \
    .tag("location", "room1") \
    .field("value", 23.5) \
    .time(datetime.utcnow())
write_api.write(bucket="sensors", record=point)

# Query data
query_api = client.query_api()
query = '''
from(bucket: "sensors")
    |> range(start: -1h)
    |> filter(fn: (r) => r._measurement == "temperature")
    |> mean()
'''
result = query_api.query(query)
```

### Pros and Cons

**Pros:**
- Optimized for time-series workloads
- Efficient compression
- Built-in downsampling
- Fast aggregations over time
- Automatic data retention

**Cons:**
- Specialized use case
- Not for general-purpose data
- Can be complex to manage
- Limited relationship handling

## Comparison Matrix

| Feature | Relational | Document | Key-Value | Wide-Column | Graph | Time-Series |
|---------|-----------|----------|-----------|-------------|-------|-------------|
| **Schema** | Rigid | Flexible | None | Flexible | Flexible | Schema-like |
| **Scalability** | Vertical | Horizontal | Horizontal | Horizontal | Variable | Horizontal |
| **Consistency** | Strong (ACID) | Configurable | Eventual | Eventual | Strong | Configurable |
| **Query Complexity** | High | Medium | Low | Medium | High | Medium |
| **Relationships** | Excellent | Good | Poor | Poor | Excellent | Poor |
| **Write Performance** | Good | Excellent | Excellent | Excellent | Good | Excellent |
| **Read Performance** | Good | Excellent | Excellent | Good | Good (traversals) | Excellent |
| **Use Case** | Transactional | Content/Apps | Caching | Analytics | Social/Networks | Monitoring |

## Specialized Database Types

### In-Memory Databases
- **Examples**: Redis, Memcached, VoltDB
- **Use**: Ultra-fast access, caching, real-time analytics
- **Trade-off**: Limited by RAM size, persistence optional

### Search Engines
- **Examples**: Elasticsearch, Apache Solr
- **Use**: Full-text search, log analytics, document search
- **Features**: Text analysis, relevance scoring, faceted search

### Vector Databases
- **Examples**: Pinecone, Weaviate, Milvus
- **Use**: ML embeddings, similarity search, AI applications
- **Features**: Nearest neighbor search, semantic search

### NewSQL Databases
- **Examples**: CockroachDB, Google Spanner, VoltDB
- **Use**: SQL with NoSQL scalability
- **Features**: ACID + horizontal scaling

## Choosing the Right Database Type

### Decision Framework

```
Start
  │
  ├─ Need ACID guarantees? ────────────→ YES ─→ Relational DB
  │                                       │
  ├─ Complex relationships? ─────────────┘
  │                                       NO
  │                                       │
  ├─ Time-series data? ──────────────→ YES ─→ Time-Series DB
  │                                       │
  ├─ Graph relationships? ───────────→ YES ─→ Graph DB
  │                                       │
  ├─ Simple key lookups? ────────────→ YES ─→ Key-Value DB
  │                                       │
  ├─ Flexible documents? ────────────→ YES ─→ Document DB
  │                                       │
  └─ High write throughput? ─────────→ YES ─→ Wide-Column DB
```

## Summary

Each database type has been designed for specific workloads:

- **Relational**: Strong consistency, complex queries, structured data
- **Document**: Flexible schemas, nested data, rapid development
- **Key-Value**: Simple, fast, caching and session storage
- **Wide-Column**: High write throughput, time-series, analytics
- **Graph**: Relationship-focused, social networks, recommendations
- **Time-Series**: Temporal data, monitoring, IoT

Modern applications often use **polyglot persistence** - multiple database types for different parts of the system.

## Next Steps

- [Why Databases Matter](./why-databases-matter.md) - Understand the impact
- [Choosing the Right Database](./choosing-database.md) - Make informed decisions
- [Part 2: Relational Databases](../02-relational-databases/README.md) - Deep dive into SQL

---

[← Previous: What Are Databases?](./what-are-databases.md) | [Next: Why Databases Matter →](./why-databases-matter.md)
