# Part 11: Scaling Databases

## Overview

As applications grow, database scaling becomes essential. This section covers strategies for scaling databases from thousands to millions of users, with practical examples and real-world considerations.

## What You'll Learn

- Vertical vs horizontal scaling
- Replication strategies (master-slave, master-master)
- Sharding and partitioning
- Load balancing
- Database clustering
- Microservices and database per service
- Caching strategies at scale
- Managing distributed transactions

## Scaling Fundamentals

### When to Scale?

**Signs you need to scale:**
- ⚠️ Query response times increasing
- ⚠️ CPU/Memory consistently above 80%
- ⚠️ Connection pool exhaustion
- ⚠️ Disk I/O bottlenecks
- ⚠️ Growing dataset size
- ⚠️ Increasing concurrent users

### Scale Up vs Scale Out

```
Vertical Scaling (Scale Up)
┌─────────────────┐
│   Single Server │
│   More CPU/RAM  │
│   Bigger Disk   │
└─────────────────┘

Pros:
✅ Simple - no application changes
✅ No data distribution complexity
✅ ACID guarantees maintained

Cons:
❌ Hardware limits (ceiling)
❌ Expensive at high end
❌ Single point of failure
❌ Downtime for upgrades

Horizontal Scaling (Scale Out)
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Server1 │  │ Server2 │  │ Server3 │
└─────────┘  └─────────┘  └─────────┘

Pros:
✅ Linear scalability
✅ No hardware ceiling
✅ High availability
✅ Cost-effective (commodity hardware)

Cons:
❌ Application complexity
❌ Data distribution challenges
❌ Eventual consistency
❌ Complex transactions
```

### Typical Scaling Journey

```
Stage 1: Single Server (0-10K users)
├── One database instance
├── Application server on same host
└── Suitable for MVP and early stage

Stage 2: Vertical Scaling (10K-100K users)
├── Separate database and application servers
├── Larger database instance
└── Add more CPU/RAM

Stage 3: Read Replicas (100K-1M users)
├── Primary database (writes)
├── Multiple read replicas (reads)
├── Load balancer for read traffic
└── Caching layer (Redis)

Stage 4: Horizontal Scaling (1M+ users)
├── Database sharding
├── Multiple primary nodes
├── Distributed caching
├── Microservices architecture
└── Multi-region deployment
```

## Replication Strategies

### Master-Replica (Primary-Secondary)

```
         ┌─────────────┐
         │   Primary   │  ← All writes
         │  (Master)   │
         └──────┬──────┘
                │
        ┌───────┴───────┐
        ├───────┬───────┤
   ┌────▼────┐ ┌▼───────┐ ┌▼────────┐
   │Replica 1│ │Replica2│ │Replica 3│  ← Read traffic distributed
   │ (Read)  │ │ (Read) │ │ (Read)  │
   └─────────┘ └────────┘ └─────────┘
```

#### PostgreSQL Replication

**Primary Server Configuration:**
```ini
# postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_size = 64  # Keep 64MB of WAL
```

**Create Replication User:**
```sql
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'strong_password';
```

**pg_hba.conf:**
```conf
# Allow replication connections
host replication replicator 10.0.1.0/24 md5
```

**Replica Server Setup:**
```bash
# Stop PostgreSQL on replica
systemctl stop postgresql

# Remove existing data
rm -rf /var/lib/postgresql/15/main

# Clone from primary
pg_basebackup -h primary-server -D /var/lib/postgresql/15/main -U replicator -P -v -R

# Start replica
systemctl start postgresql
```

#### Application-Level Read/Write Splitting

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseRouter:
    """Route queries to primary or replicas"""

    def __init__(self):
        # Primary (write) connection
        self.primary = create_engine('postgresql://user:pass@primary:5432/db')

        # Replica (read) connections
        self.replicas = [
            create_engine('postgresql://user:pass@replica1:5432/db'),
            create_engine('postgresql://user:pass@replica2:5432/db'),
            create_engine('postgresql://user:pass@replica3:5432/db'),
        ]

        self.replica_index = 0

    def get_write_engine(self):
        """Get primary engine for writes"""
        return self.primary

    def get_read_engine(self):
        """Get replica engine for reads (round-robin)"""
        engine = self.replicas[self.replica_index]
        self.replica_index = (self.replica_index + 1) % len(self.replicas)
        return engine

# Usage
router = DatabaseRouter()

# Write operation
write_session = sessionmaker(bind=router.get_write_engine())()
new_user = User(username='john', email='john@example.com')
write_session.add(new_user)
write_session.commit()

# Read operation
read_session = sessionmaker(bind=router.get_read_engine())()
users = read_session.query(User).all()
```

### MongoDB Replica Sets

```javascript
// Initialize replica set
rs.initiate({
  _id: "myReplicaSet",
  members: [
    { _id: 0, host: "mongodb1:27017", priority: 2 },  // Primary
    { _id: 1, host: "mongodb2:27017", priority: 1 },  // Secondary
    { _id: 2, host: "mongodb3:27017", priority: 1 }   // Secondary
  ]
})

// Check status
rs.status()

// Add member
rs.add("mongodb4:27017")

// Remove member
rs.remove("mongodb4:27017")
```

**Python with MongoDB Replica Set:**
```python
from pymongo import MongoClient, ReadPreference

# Connect to replica set
client = MongoClient(
    'mongodb://mongodb1:27017,mongodb2:27017,mongodb3:27017/',
    replicaSet='myReplicaSet',
    readPreference=ReadPreference.SECONDARY_PREFERRED
)

db = client['myapp']

# Write goes to primary
db.users.insert_one({'username': 'john'})

# Reads can go to secondaries
users = db.users.find().read_preference(ReadPreference.SECONDARY)

# Force read from primary
users = db.users.find().read_preference(ReadPreference.PRIMARY)
```

## Sharding and Partitioning

### What is Sharding?

Sharding distributes data across multiple database servers based on a shard key.

```
Users Table Sharded by user_id

Shard 1 (user_id % 4 == 0)     Shard 2 (user_id % 4 == 1)
┌──────────────────┐           ┌──────────────────┐
│ user_id: 4, 8, 12│           │ user_id: 1, 5, 9 │
└──────────────────┘           └──────────────────┘

Shard 3 (user_id % 4 == 2)     Shard 4 (user_id % 4 == 3)
┌──────────────────┐           ┌──────────────────┐
│ user_id: 2, 6, 10│           │ user_id: 3, 7, 11│
└──────────────────┘           └──────────────────┘
```

### Sharding Strategies

#### 1. Range-Based Sharding

```python
# Shard by user_id ranges
SHARDS = {
    'shard1': {'min': 0, 'max': 1000000},
    'shard2': {'min': 1000001, 'max': 2000000},
    'shard3': {'min': 2000001, 'max': 3000000},
    'shard4': {'min': 3000001, 'max': float('inf')},
}

def get_shard(user_id):
    """Determine shard based on user_id"""
    for shard_name, shard_range in SHARDS.items():
        if shard_range['min'] <= user_id <= shard_range['max']:
            return shard_name
    raise ValueError(f"No shard found for user_id: {user_id}")

def get_user(user_id):
    """Retrieve user from appropriate shard"""
    shard = get_shard(user_id)
    conn = shard_connections[shard]
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()

# Pros:
# ✅ Range queries efficient on single shard
# ✅ Simple to understand

# Cons:
# ❌ Uneven distribution (hotspots)
# ❌ Rebalancing required as data grows
```

#### 2. Hash-Based Sharding

```python
def get_shard_hash(user_id, num_shards=4):
    """Determine shard using hash function"""
    return user_id % num_shards

# More even distribution
user_1 → shard 1 (1 % 4 = 1)
user_2 → shard 2 (2 % 4 = 2)
user_3 → shard 3 (3 % 4 = 3)
user_4 → shard 0 (4 % 4 = 0)
user_5 → shard 1 (5 % 4 = 1)

# Pros:
# ✅ Even distribution
# ✅ No hotspots

# Cons:
# ❌ Range queries require checking all shards
# ❌ Difficult to rebalance (resharding)
```

#### 3. Consistent Hashing

```python
import hashlib

class ConsistentHash:
    """Consistent hashing for sharding"""

    def __init__(self, nodes, virtual_nodes=150):
        self.ring = {}
        self.sorted_keys = []
        self.nodes = nodes
        self.virtual_nodes = virtual_nodes

        for node in nodes:
            self.add_node(node)

    def _hash(self, key):
        """Hash function"""
        return int(hashlib.md5(str(key).encode()).hexdigest(), 16)

    def add_node(self, node):
        """Add node to ring"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node
            self.sorted_keys.append(hash_value)

        self.sorted_keys.sort()

    def remove_node(self, node):
        """Remove node from ring"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            del self.ring[hash_value]
            self.sorted_keys.remove(hash_value)

    def get_node(self, key):
        """Get node for key"""
        if not self.ring:
            return None

        hash_value = self._hash(key)

        # Find first node clockwise from hash
        for ring_key in self.sorted_keys:
            if ring_key >= hash_value:
                return self.ring[ring_key]

        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]

# Usage
shards = ['shard1', 'shard2', 'shard3', 'shard4']
ch = ConsistentHash(shards)

# Get shard for user
shard = ch.get_node('user_12345')

# Add new shard (only affects ~25% of keys)
ch.add_node('shard5')

# Pros:
# ✅ Even distribution
# ✅ Minimal rebalancing when adding/removing nodes
# ✅ Scales well

# Cons:
# ❌ More complex to implement
# ❌ Range queries still difficult
```

### Application-Level Sharding

```python
class ShardedDatabase:
    """Sharded database connection manager"""

    def __init__(self, shard_configs):
        self.shards = {}
        for shard_name, config in shard_configs.items():
            self.shards[shard_name] = psycopg2.connect(**config)

        self.num_shards = len(self.shards)

    def get_shard(self, user_id):
        """Get shard connection for user_id"""
        shard_id = user_id % self.num_shards
        shard_name = f'shard{shard_id}'
        return self.shards[shard_name]

    def get_user(self, user_id):
        """Get user from appropriate shard"""
        conn = self.get_shard(user_id)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()

    def create_user(self, user_id, username, email):
        """Create user in appropriate shard"""
        conn = self.get_shard(user_id)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (id, username, email)
            VALUES (%s, %s, %s)
        """, (user_id, username, email))
        conn.commit()

    def get_users_by_emails(self, emails):
        """Query across all shards"""
        results = []
        for shard_name, conn in self.shards.items():
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users WHERE email = ANY(%s)
            """, (emails,))
            results.extend(cursor.fetchall())
        return results

# Configuration
shard_configs = {
    'shard0': {'host': 'db1.example.com', 'database': 'myapp_shard0', 'user': 'app', 'password': 'pass'},
    'shard1': {'host': 'db2.example.com', 'database': 'myapp_shard1', 'user': 'app', 'password': 'pass'},
    'shard2': {'host': 'db3.example.com', 'database': 'myapp_shard2', 'user': 'app', 'password': 'pass'},
    'shard3': {'host': 'db4.example.com', 'database': 'myapp_shard3', 'user': 'app', 'password': 'pass'},
}

db = ShardedDatabase(shard_configs)

# Usage
user = db.get_user(user_id=12345)
db.create_user(user_id=12346, username='john', email='john@example.com')
```

### PostgreSQL: Native Partitioning

```sql
-- Create partitioned table (PostgreSQL 10+)
CREATE TABLE orders (
    order_id BIGSERIAL,
    user_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    total DECIMAL(10, 2),
    PRIMARY KEY (order_id, order_date)
) PARTITION BY RANGE (order_date);

-- Create partitions
CREATE TABLE orders_2023 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE orders_2025 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Queries automatically route to appropriate partition
SELECT * FROM orders WHERE order_date = '2024-06-15';
-- Only scans orders_2024 partition

-- Benefits:
-- ✅ Faster queries (smaller tables)
-- ✅ Easier maintenance (drop old partitions)
-- ✅ Better index performance
```

### MongoDB Sharding

```javascript
// Enable sharding on database
sh.enableSharding("myapp")

// Shard collection by user_id (hashed)
sh.shardCollection("myapp.users", { user_id: "hashed" })

// Or by range
sh.shardCollection("myapp.orders", { order_date: 1 })

// Check shard distribution
db.users.getShardDistribution()

// Output:
// Shard shard0000 at shard0000/mongo1:27017
//   data: 10.2GB docs: 5000000
//
// Shard shard0001 at shard0001/mongo2:27017
//   data: 10.1GB docs: 4980000
//
// Totals
//   data: 20.3GB docs: 9980000
```

## Load Balancing

### Database Load Balancer

```
Client Application
        │
        ▼
┌───────────────┐
│ Load Balancer │
│   (HAProxy)   │
└───────┬───────┘
        │
   ┌────┴────┬─────────┐
   │         │         │
   ▼         ▼         ▼
┌──────┐ ┌──────┐ ┌──────┐
│Read  │ │Read  │ │Read  │
│Replica│ │Replica│ │Replica│
└──────┘ └──────┘ └──────┘
```

**HAProxy Configuration:**
```conf
# /etc/haproxy/haproxy.cfg

global
    maxconn 4096

defaults
    mode tcp
    timeout connect 5s
    timeout client 30s
    timeout server 30s

# PostgreSQL read replicas
frontend postgres_read
    bind *:5433
    default_backend postgres_read_replicas

backend postgres_read_replicas
    balance roundrobin
    option pgsql-check user haproxy
    server replica1 10.0.1.11:5432 check
    server replica2 10.0.1.12:5432 check
    server replica3 10.0.1.13:5432 check
```

### Connection Pooling at Scale

```python
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool
import time

# Configure connection pool
engine = create_engine(
    'postgresql://user:pass@host/db',
    poolclass=QueuePool,
    pool_size=20,          # Connections per process
    max_overflow=40,       # Additional connections when needed
    pool_timeout=30,       # Wait time for connection
    pool_recycle=1800,     # Recycle after 30 minutes
    pool_pre_ping=True,    # Test connection before using
)

# Monitor pool
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    print(f"New connection established")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    print(f"Connection checked out from pool")

# With multiple application servers:
# 10 app servers × 20 connections = 200 total connections
# Ensure database max_connections > 200
```

## Microservices and Database per Service

### Pattern: Database per Service

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   User       │  │   Order      │  │   Inventory  │
│   Service    │  │   Service    │  │   Service    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐
│   User DB    │  │   Order DB   │  │ Inventory DB │
│ (PostgreSQL) │  │  (MongoDB)   │  │ (PostgreSQL) │
└──────────────┘  └──────────────┘  └──────────────┘
```

**Benefits:**
- ✅ Service independence
- ✅ Technology choice per service
- ✅ Independent scaling
- ✅ Fault isolation

**Challenges:**
- ❌ Distributed transactions
- ❌ Data consistency
- ❌ Cross-service queries
- ❌ Increased complexity

### Saga Pattern for Distributed Transactions

```python
class OrderSaga:
    """Saga pattern for distributed transaction"""

    def create_order(self, user_id, items, total):
        """
        Create order across multiple services:
        1. Reserve inventory
        2. Process payment
        3. Create order
        4. Update user stats
        """
        compensations = []

        try:
            # Step 1: Reserve inventory
            inventory_reservation = inventory_service.reserve(items)
            compensations.append(lambda: inventory_service.release(inventory_reservation))

            # Step 2: Process payment
            payment = payment_service.charge(user_id, total)
            compensations.append(lambda: payment_service.refund(payment))

            # Step 3: Create order
            order = order_service.create(user_id, items, total)
            compensations.append(lambda: order_service.cancel(order))

            # Step 4: Update user stats
            user_service.increment_order_count(user_id)

            return order

        except Exception as e:
            # Compensate in reverse order
            for compensate in reversed(compensations):
                try:
                    compensate()
                except Exception as comp_error:
                    # Log compensation failure
                    logger.error(f"Compensation failed: {comp_error}")

            raise
```

## Caching at Scale

### Multi-Level Caching

```
┌─────────────────────────────────────────┐
│        Application Server               │
│  ┌─────────────────────────────────┐   │
│  │   L1: In-Memory Cache (LRU)     │   │
│  │   - Frequently accessed data     │   │
│  │   - 5-10 second TTL              │   │
│  └─────────────┬───────────────────┘   │
└────────────────┼───────────────────────┘
                 │ Cache miss
                 ▼
┌────────────────────────────────────────┐
│         L2: Redis Cluster              │
│  ┌─────────────────────────────────┐  │
│  │  Distributed Cache               │  │
│  │  - Shared across app servers     │  │
│  │  - 5-60 minute TTL               │  │
│  └─────────────┬───────────────────┘  │
└────────────────┼───────────────────────┘
                 │ Cache miss
                 ▼
┌────────────────────────────────────────┐
│         L3: Database                   │
│  - PostgreSQL with replicas            │
│  - Source of truth                     │
└────────────────────────────────────────┘
```

```python
from functools import lru_cache
import redis
import json

# L1: In-memory cache
@lru_cache(maxsize=1000)
def get_user_l1(user_id):
    """L1 cache: In-memory"""
    return get_user_l2(user_id)

# L2: Redis cache
r = redis.Redis(host='redis-cluster', port=6379, decode_responses=True)

def get_user_l2(user_id):
    """L2 cache: Redis"""
    cache_key = f'user:{user_id}'

    # Try Redis
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # L3: Database
    user = get_user_from_db(user_id)

    # Store in Redis (5 minutes)
    r.setex(cache_key, 300, json.dumps(user))

    return user

def get_user_from_db(user_id):
    """L3: Database query"""
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()

# Invalidation: Clear all cache levels
def invalidate_user(user_id):
    # Clear L1
    get_user_l1.cache_clear()

    # Clear L2
    r.delete(f'user:{user_id}')
```

## Monitoring and Observability

### Key Metrics to Monitor

```python
import time
from prometheus_client import Counter, Histogram, Gauge

# Database metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type', 'shard']
)

db_connections = Gauge(
    'db_active_connections',
    'Active database connections',
    ['shard']
)

db_errors = Counter(
    'db_errors_total',
    'Database errors',
    ['error_type', 'shard']
)

# Instrument queries
def query_with_metrics(query, params, shard='primary'):
    start = time.time()

    try:
        cursor.execute(query, params)
        result = cursor.fetchall()

        duration = time.time() - start
        db_query_duration.labels(
            query_type='select' if query.upper().startswith('SELECT') else 'write',
            shard=shard
        ).observe(duration)

        return result

    except Exception as e:
        db_errors.labels(
            error_type=type(e).__name__,
            shard=shard
        ).inc()
        raise
```

## Summary

Scaling databases requires:

### Start Simple
- Begin with vertical scaling
- Add read replicas when needed
- Implement caching early

### Scale Horizontally
- Shard when single server insufficient
- Use consistent hashing for even distribution
- Plan for rebalancing

### Architecture Patterns
- Database per service for microservices
- Saga pattern for distributed transactions
- Multi-level caching

### Monitor Everything
- Query performance
- Connection pool utilization
- Replication lag
- Shard distribution

### Best Practices
- Design for scalability from start
- Test scaling strategies before needed
- Automate deployment and monitoring
- Plan for data migration

## Next Steps

- [Performance Optimization](../09-performance/README.md) - Optimize before scaling
- [Security at Scale](../10-security/README.md) - Secure distributed systems
- [Deployment Strategies](../08-deployment/README.md) - Deploy scaled architecture

---

[← Previous: Security](../10-security/README.md) | [Back to Main](../README.md)
