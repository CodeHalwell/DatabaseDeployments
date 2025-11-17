# Choosing the Right Database

## Introduction

Selecting the appropriate database is one of the most critical architectural decisions you'll make. The wrong choice can lead to performance bottlenecks, scalability issues, and significant technical debt. This guide provides a framework for making informed database decisions.

## Decision Framework

### Step 1: Understand Your Requirements

#### Data Structure
**Questions to ask:**
- Is my data highly structured or flexible?
- Do I have complex relationships between entities?
- Will my schema change frequently?
- Do I need nested or hierarchical data?

**Example Analysis:**
```
Use Case: E-commerce Product Catalog

Data Characteristics:
✓ Products have varying attributes (clothing vs electronics)
✓ Schema evolves with new product categories
✓ Nested data (product variants, reviews, specifications)
✓ Flexible structure needed

Recommendation: Document Database (MongoDB)
- Flexible schema for varying products
- Native support for nested data
- Easy to add new product types
```

#### Access Patterns
**Questions to ask:**
- How will data be queried (by key, range, full-text search)?
- Read-heavy or write-heavy workload?
- Need for real-time analytics?
- Complex joins or simple lookups?

**Example Analysis:**
```
Use Case: Session Storage for Web Application

Access Patterns:
✓ Lookup by session ID (key-based access)
✓ High read/write frequency
✓ Short-lived data (expires after inactivity)
✓ No complex queries needed

Recommendation: Key-Value Store (Redis)
- O(1) lookups by key
- Built-in expiration (TTL)
- In-memory for maximum speed
- Perfect for ephemeral data
```

#### Consistency Requirements
**Questions to ask:**
- Do I need immediate consistency or is eventual consistency acceptable?
- Are financial transactions involved?
- Can I tolerate temporary inconsistencies?
- Do I need distributed transactions?

**CAP Theorem Considerations:**
```
High Consistency Required:
├─ Banking/Financial: PostgreSQL, MySQL
├─ Inventory Management: PostgreSQL + Redis
└─ Order Processing: SQL Server, Oracle

Eventual Consistency Acceptable:
├─ Social Media Feeds: Cassandra, DynamoDB
├─ Analytics Data: ClickHouse, BigQuery
└─ Logging/Monitoring: Elasticsearch, InfluxDB
```

#### Scale Requirements
**Questions to ask:**
- Current data size and growth rate?
- Expected number of concurrent users?
- Geographic distribution of users?
- Need for horizontal scalability?

**Scale Planning:**
```
Small Scale (<1M records, <100 concurrent users)
→ Single PostgreSQL or MySQL instance
→ Simple backup strategy
→ Cost: $50-200/month

Medium Scale (1M-100M records, 100-10K users)
→ Primary database + read replicas
→ Redis caching layer
→ Regular backups + monitoring
→ Cost: $500-2000/month

Large Scale (>100M records, >10K users)
→ Sharded database architecture
→ Multi-region deployment
→ CDN + multiple cache layers
→ Advanced monitoring and automation
→ Cost: $5000+/month
```

### Step 2: Evaluate Database Categories

#### Decision Tree

```
START
  │
  ├─ Need ACID transactions? ──────────── YES ─→ Relational DB
  │   └─ Example: Banking, e-commerce checkout      │
  │                                                  NO
  │                                                  ↓
  ├─ Primary access pattern?
  │   │
  │   ├─ Key-based lookups ────────────────────→ Key-Value Store
  │   │   └─ Example: Sessions, cache              (Redis, DynamoDB)
  │   │
  │   ├─ Complex relationships ────────────────→ Graph Database
  │   │   └─ Example: Social networks              (Neo4j, Neptune)
  │   │
  │   ├─ Time-series data ─────────────────────→ Time-Series DB
  │   │   └─ Example: Metrics, IoT                 (InfluxDB, TimescaleDB)
  │   │
  │   ├─ Flexible documents ───────────────────→ Document Store
  │   │   └─ Example: CMS, catalogs                (MongoDB, CouchDB)
  │   │
  │   ├─ High write throughput ────────────────→ Wide-Column Store
  │   │   └─ Example: Analytics, logs              (Cassandra, HBase)
  │   │
  │   └─ Full-text search ─────────────────────→ Search Engine
  │       └─ Example: Product search               (Elasticsearch, Solr)
  │
  └─ Multi-model requirements? ────────────── YES ─→ Polyglot Persistence
      └─ Example: Use multiple databases            (Combine multiple types)
```

## Common Use Cases and Recommendations

### Use Case 1: E-Commerce Platform

**Requirements:**
- Product catalog with varying attributes
- User accounts and order history
- Shopping cart management
- Inventory tracking
- Search functionality
- Real-time analytics

**Recommended Architecture:**
```python
class ECommerceStack:
    """
    Polyglot persistence for e-commerce
    """
    # Product Catalog - Flexible schema, nested data
    products_db = MongoDB

    # User accounts, orders - ACID transactions
    transactional_db = PostgreSQL

    # Session storage, shopping carts - Fast access, TTL
    cache_db = Redis

    # Product search - Full-text search
    search_db = Elasticsearch

    # Analytics - High write throughput, time-series
    analytics_db = ClickHouse

# Product Catalog (MongoDB)
product = {
    '_id': 'PROD123',
    'name': 'Wireless Headphones',
    'category': 'Electronics',
    'specs': {
        'battery_life': '30 hours',
        'bluetooth': '5.0',
        'noise_cancellation': True
    },
    'variants': [
        {'color': 'black', 'sku': 'WH-BLK', 'stock': 50},
        {'color': 'white', 'sku': 'WH-WHT', 'stock': 30}
    ],
    'reviews': [...]
}

# Orders (PostgreSQL)
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP
);

# Shopping Cart (Redis)
redis.hset('cart:user123', 'PROD123', 2)  # 2 quantity
redis.expire('cart:user123', 86400)  # 24 hour TTL

# Product Search (Elasticsearch)
es.index('products', {
    'name': 'Wireless Headphones',
    'description': 'Premium noise-canceling...',
    'price': 199.99,
    'category': 'Electronics'
})
```

**Benefits:**
- Each database optimized for its specific role
- MongoDB handles flexible product schemas
- PostgreSQL ensures transactional integrity
- Redis provides fast cart access
- Elasticsearch enables powerful search

### Use Case 2: Social Media Platform

**Requirements:**
- User profiles and authentication
- Friend/follower relationships
- News feed generation
- Real-time notifications
- Media storage
- Analytics and insights

**Recommended Architecture:**
```python
class SocialMediaStack:
    # User profiles - Structured data, authentication
    user_db = PostgreSQL

    # Relationships - Graph queries
    graph_db = Neo4j

    # News feeds - Time-ordered, high volume
    feed_db = Cassandra

    # Real-time cache - Online users, recent activity
    cache_db = Redis

    # Media metadata - Flexible documents
    media_db = MongoDB

    # Object storage - Actual media files
    object_storage = S3

# User Profile (PostgreSQL)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP
);

# Relationships (Neo4j)
MATCH (user:User {username: 'john'})-[:FOLLOWS]->(following)
      -[:FOLLOWS]->(recommendation)
WHERE NOT (user)-[:FOLLOWS]->(recommendation)
RETURN recommendation
LIMIT 10;

# News Feed (Cassandra)
CREATE TABLE user_feed (
    user_id UUID,
    post_time TIMESTAMP,
    post_id UUID,
    author_id UUID,
    content TEXT,
    PRIMARY KEY ((user_id), post_time)
) WITH CLUSTERING ORDER BY (post_time DESC);

# Real-time Presence (Redis)
redis.setex(f'online:{user_id}', 300, '1')  # 5-minute presence
redis.zadd('active_users', {user_id: timestamp})
```

### Use Case 3: Financial Trading Platform

**Requirements:**
- Absolute data consistency
- ACID transactions
- Audit trails
- High availability
- Real-time processing
- Regulatory compliance

**Recommended Architecture:**
```python
class TradingPlatformStack:
    # Core transactions - Maximum consistency
    transactional_db = PostgreSQL  # or Oracle for enterprise

    # Real-time market data - Time-series
    market_data_db = TimescaleDB

    # Cache layer - Price quotes, user sessions
    cache_db = Redis

    # Audit logs - Immutable records
    audit_db = PostgreSQL  # Separate instance

# Account Management (PostgreSQL with Serializable Isolation)
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Atomic account update with locking
UPDATE accounts
SET balance = balance - :trade_amount,
    updated_at = NOW()
WHERE user_id = :user_id
  AND balance >= :trade_amount
RETURNING balance;

-- Record transaction
INSERT INTO transactions (
    user_id, type, amount, symbol, price, timestamp
) VALUES (
    :user_id, 'BUY', :amount, :symbol, :price, NOW()
);

-- Audit trail (append-only)
INSERT INTO audit_log (
    user_id, action, details, ip_address, timestamp
) VALUES (
    :user_id, 'TRADE_EXECUTED', :details, :ip, NOW()
);

COMMIT;

# Market Data (TimescaleDB)
CREATE TABLE stock_prices (
    timestamp TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    price DECIMAL(10,2),
    volume BIGINT
);

SELECT create_hypertable('stock_prices', 'timestamp');

# Real-time Quotes (Redis)
redis.zadd('prices', {
    'AAPL': 150.25,
    'GOOGL': 2800.50,
    'MSFT': 310.75
})
```

**Why This Stack:**
- PostgreSQL/Oracle provides ACID guarantees
- TimescaleDB optimizes time-series queries
- Redis enables real-time quote distribution
- Separate audit database ensures compliance

### Use Case 4: IoT Monitoring System

**Requirements:**
- Millions of sensor data points
- Time-series data
- Real-time alerting
- Historical analysis
- Data retention policies
- Downsampling for long-term storage

**Recommended Architecture:**
```python
class IoTStack:
    # Time-series data - Optimized for timestamps
    metrics_db = InfluxDB

    # Device metadata - Flexible documents
    device_db = MongoDB

    # Real-time processing - Streaming
    stream_processor = Apache_Kafka + InfluxDB

    # Alerts and rules - Fast lookups
    cache_db = Redis

# Sensor Data (InfluxDB)
from influxdb_client import Point

# Write sensor data
point = Point("temperature") \
    .tag("sensor_id", "TEMP001") \
    .tag("location", "warehouse_a") \
    .tag("zone", "freezer") \
    .field("celsius", -18.5) \
    .field("humidity", 65) \
    .time(datetime.utcnow())

write_api.write(bucket="sensors", record=point)

# Query aggregated data
query = '''
from(bucket: "sensors")
    |> range(start: -24h)
    |> filter(fn: (r) => r._measurement == "temperature")
    |> filter(fn: (r) => r.location == "warehouse_a")
    |> aggregateWindow(every: 1h, fn: mean)
'''

# Automatic downsampling (saves storage)
# Raw data: 1 second intervals → Keep 7 days
# 1 minute averages → Keep 30 days
# 1 hour averages → Keep 1 year
# Daily averages → Keep forever

# Device Configuration (MongoDB)
device = {
    '_id': 'TEMP001',
    'type': 'temperature_sensor',
    'location': {
        'warehouse': 'warehouse_a',
        'zone': 'freezer',
        'coordinates': {'lat': 42.3601, 'lon': -71.0589}
    },
    'thresholds': {
        'min_temp': -20,
        'max_temp': -15,
        'alert_delay': 300  # 5 minutes
    },
    'calibration': {
        'last_calibrated': ISODate('2024-01-01'),
        'offset': 0.5
    }
}

# Real-time Alerts (Redis)
# Check threshold violations
current_temp = influx.get_latest('TEMP001')
threshold = redis.hget('device:TEMP001', 'max_temp')

if current_temp > threshold:
    redis.zadd('active_alerts', {
        'TEMP001:high_temp': timestamp
    })
    # Trigger notification system
```

### Use Case 5: Content Management System

**Requirements:**
- Flexible content structures
- Version control
- Media library
- Search functionality
- Multi-language support
- User permissions

**Recommended Architecture:**
```python
class CMSStack:
    # Content storage - Flexible schemas
    content_db = MongoDB

    # User management - Structured, ACID
    user_db = PostgreSQL

    # Search - Full-text search
    search_db = Elasticsearch

    # Media files - Object storage
    media_storage = S3

    # Cache - Published pages
    cache_db = Redis

# Content (MongoDB)
article = {
    '_id': ObjectId(),
    'slug': 'introduction-to-databases',
    'title': {
        'en': 'Introduction to Databases',
        'es': 'Introducción a las Bases de Datos',
        'fr': 'Introduction aux Bases de Données'
    },
    'content': {
        'en': 'Databases are...',
        'es': 'Las bases de datos son...',
        'fr': 'Les bases de données sont...'
    },
    'metadata': {
        'author_id': ObjectId('...'),
        'category': 'Technology',
        'tags': ['databases', 'tutorial', 'beginner'],
        'featured_image': 's3://bucket/image.jpg',
        'seo': {
            'description': '...',
            'keywords': ['database', 'SQL', 'NoSQL']
        }
    },
    'versions': [
        {
            'version': 1,
            'created_at': ISODate('2024-01-01'),
            'created_by': ObjectId('...'),
            'content': '...'
        },
        {
            'version': 2,
            'created_at': ISODate('2024-01-15'),
            'created_by': ObjectId('...'),
            'content': '...'
        }
    ],
    'status': 'published',
    'published_at': ISODate('2024-01-15'),
    'updated_at': ISODate('2024-01-15')
}

# Search Index (Elasticsearch)
es.index('articles', {
    'slug': article['slug'],
    'title': article['title']['en'],
    'content': article['content']['en'],
    'tags': article['metadata']['tags'],
    'published_at': article['published_at']
})

# Cache Published Pages (Redis)
redis.setex(
    f'page:{article["slug"]}:en',
    3600,
    render_article(article, lang='en')
)
```

## Evaluation Criteria Matrix

### Performance Characteristics

| Database Type | Read Speed | Write Speed | Query Complexity | Scalability |
|--------------|-----------|-------------|------------------|-------------|
| **Relational** | Good | Good | Excellent | Vertical (primary) |
| **Document** | Excellent | Excellent | Good | Horizontal |
| **Key-Value** | Excellent | Excellent | Limited | Horizontal |
| **Wide-Column** | Good | Excellent | Medium | Horizontal |
| **Graph** | Good (paths) | Good | Excellent (relationships) | Variable |
| **Time-Series** | Excellent (time ranges) | Excellent | Good (aggregations) | Horizontal |

### Operational Considerations

| Factor | Questions to Ask | Impact on Choice |
|--------|-----------------|------------------|
| **Cost** | What's the budget? Managed vs self-hosted? | Cloud managed services cost more but reduce operational overhead |
| **Expertise** | What does the team know? Learning curve? | Stick with familiar tech unless benefits outweigh learning costs |
| **Ecosystem** | Available tools, libraries, community? | Mature ecosystems = faster development |
| **Vendor Lock-in** | Open source vs proprietary? | Consider exit strategy and portability |
| **Maintenance** | Who will manage it? Backup strategy? | Managed services reduce operational burden |
| **Compliance** | Regulatory requirements? Data residency? | Some databases have better compliance certifications |

## Common Mistakes to Avoid

### 1. Over-Engineering
```
❌ Bad: Using a complex distributed database for a small application
✓ Good: Start with a single PostgreSQL instance, scale when needed

Example:
- Small blog with <10K users
- Chose Cassandra cluster (3+ nodes)
- Result: Complexity overhead, slow development, high costs

Better:
- PostgreSQL on a $50/month server
- Scale to read replicas if needed
- Migrate only if requirements change
```

### 2. Under-Engineering
```
❌ Bad: Using SQLite for a multi-user web application
✓ Good: Use a proper client-server database from the start

Example:
- E-commerce site using SQLite
- Result: File locking issues, poor concurrency, crashes

Better:
- Start with PostgreSQL or MySQL
- Proper concurrent access handling
- Room to scale
```

### 3. Ignoring Access Patterns
```
❌ Bad: Choosing a database before understanding queries
✓ Good: Analyze access patterns first

Example:
- Social media feed using PostgreSQL
- Complex joins for each feed request
- Result: Slow feed generation (seconds per page)

Better:
- Use Cassandra or DynamoDB
- Pre-compute feeds, optimized for time-based queries
- Result: Fast feed generation (milliseconds)
```

### 4. Ignoring Consistency Requirements
```
❌ Bad: Using eventually consistent database for financial transactions
✓ Good: Strong consistency for critical data

Example:
- E-commerce checkout using DynamoDB
- Result: Double-charged customers, inventory conflicts

Better:
- PostgreSQL for orders and payments (ACID)
- DynamoDB for product catalog (can be eventual)
- Separate concerns based on consistency needs
```

### 5. Premature Optimization
```
❌ Bad: Implementing sharding before you need it
✓ Good: Scale vertically first, then horizontally

Typical scaling path:
1. Single database instance (up to ~100K users)
2. Add read replicas (up to ~1M users)
3. Add caching layer (up to ~10M users)
4. Implement sharding (>10M users)

Don't jump to step 4 on day 1!
```

## Migration Considerations

### When to Change Databases

**Good Reasons:**
- Current database can't meet performance requirements
- Scaling costs become prohibitive
- Access patterns have fundamentally changed
- Technology limitations blocking features

**Bad Reasons:**
- "MongoDB is trendy"
- "We want to learn new technology"
- Minor performance issues (optimize first!)
- Following competitor's tech stack blindly

### Migration Strategy

```python
# Phased migration approach
class DatabaseMigration:
    """
    Gradual migration minimizes risk
    """

    # Phase 1: Dual-write
    def write_data(self, data):
        # Write to both old and new databases
        old_db.write(data)
        new_db.write(data)  # Shadow write

    # Phase 2: Verification
    def verify_consistency(self):
        # Compare old and new databases
        # Ensure data integrity
        # Fix any discrepancies

    # Phase 3: Dual-read
    def read_data(self, key):
        # Read from new database
        result = new_db.read(key)
        # Verify against old (don't return old data)
        verify(result, old_db.read(key))
        return result

    # Phase 4: Cutover
    def final_cutover(self):
        # Stop writing to old database
        # New database is primary
        # Keep old database as backup

    # Phase 5: Decommission
    def cleanup(self):
        # Verify stability
        # Archive old database
        # Deallocate resources
```

## Summary: Decision Checklist

### Before Choosing a Database:

1. **Understand Requirements**
   - [ ] Data structure and schema flexibility
   - [ ] Access patterns (read/write ratio, query types)
   - [ ] Consistency requirements
   - [ ] Scale expectations (current and future)
   - [ ] Budget constraints

2. **Evaluate Options**
   - [ ] Match database type to use case
   - [ ] Consider operational complexity
   - [ ] Assess team expertise
   - [ ] Review ecosystem and tooling
   - [ ] Check compliance requirements

3. **Proof of Concept**
   - [ ] Build prototype with realistic data
   - [ ] Test critical queries
   - [ ] Measure performance
   - [ ] Evaluate developer experience

4. **Production Readiness**
   - [ ] Backup and recovery strategy
   - [ ] Monitoring and alerting
   - [ ] Security configuration
   - [ ] Scaling plan
   - [ ] Documentation

### Red Flags

🚩 "We'll use X because everyone else does"
🚩 "We'll figure out scaling later"
🚩 "One database can do everything"
🚩 "We don't need to test performance"
🚩 "Backups aren't important yet"

## Recommended Default Choices

### For Most Applications

**Primary Database: PostgreSQL**
- Mature and reliable
- ACID compliant
- Excellent query capabilities
- Good performance
- Rich ecosystem

**Caching: Redis**
- Fast key-value access
- Multiple data structures
- Pub/sub capabilities
- Easy to integrate

**Search: Elasticsearch** (if needed)
- Powerful full-text search
- Analytics capabilities
- Horizontal scaling

### Add Specialized Databases As Needed

```
Start simple → Add complexity only when necessary

PostgreSQL + Redis = 90% of use cases covered
Add MongoDB for flexible schemas
Add Cassandra for massive write throughput
Add Neo4j for complex relationships
Add InfluxDB for time-series data
```

## Next Steps

Now that you understand how to choose a database:

1. **Relational Databases**: [Part 2: Relational Databases](../02-relational-databases/README.md)
2. **NoSQL Databases**: [Part 3: Non-Relational Databases](../03-non-relational-databases/README.md)
3. **Get Hands-On**: [Part 4: Setup and Configuration](../04-setup-and-configuration/README.md)
4. **Connect to Applications**: [Part 5: Backend Connectivity](../05-backend-connectivity/README.md)

---

[← Previous: Why Databases Matter](./why-databases-matter.md) | [Back to Fundamentals](./README.md) | [Next: Relational Databases →](../02-relational-databases/README.md)
