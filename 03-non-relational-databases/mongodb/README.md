# MongoDB: Document Database

## Overview

MongoDB is the most popular NoSQL document database, storing data in flexible, JSON-like documents. It combines the flexibility of NoSQL with powerful querying capabilities.

## What is MongoDB?

**MongoDB** stores data as documents in BSON (Binary JSON) format, allowing for:
- **Flexible schemas** - documents in the same collection can have different fields
- **Nested data** - documents can contain arrays and sub-documents
- **Rich queries** - support for complex queries, aggregations, and indexing
- **Horizontal scalability** - built-in sharding for distributed data

### Key Concepts

```
Database (database instance)
  └── Collections (like tables)
       └── Documents (like rows, but flexible)
            └── Fields (key-value pairs)
```

**Example Document:**
```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439011"),
  username: "johndoe",
  email: "john@example.com",
  profile: {
    firstName: "John",
    lastName: "Doe",
    age: 30
  },
  interests: ["databases", "python", "cloud"],
  registered: ISODate("2024-01-01T00:00:00Z")
}
```

## When to Use MongoDB

### Ideal Use Cases

✅ **Content Management Systems**
- Flexible content types (articles, videos, products)
- Varying attributes per content type
- Nested comments and metadata

✅ **Product Catalogs**
- Products with different specifications
- Hierarchical categories
- Dynamic attributes (size, color, etc.)

✅ **User Profiles**
- Varying user data fields
- Nested preferences and settings
- Activity history

✅ **Real-Time Analytics**
- Event tracking and logging
- Time-series data with flexible schema
- Aggregation pipelines for analysis

✅ **Mobile Applications**
- Offline-first apps
- Flexible data synchronization
- Document-based data model

✅ **Internet of Things (IoT)**
- Sensor data with varying fields
- Time-series measurements
- Device metadata

### When NOT to Use MongoDB

❌ **Financial Transactions** (use PostgreSQL/MySQL)
- Need ACID guarantees across multiple records
- Complex multi-table transactions

❌ **Complex Relationships** (use relational or graph DB)
- Heavy use of joins
- Normalized data required

❌ **Fixed Schema Requirements**
- Schema strictly enforced
- Relationships more important than document flexibility

## Installation and Setup

### Local Installation

**macOS:**
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

**Ubuntu:**
```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Create list file
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

**Windows:**
```powershell
# Download from https://www.mongodb.com/try/download/community
# Run installer and follow prompts
# MongoDB Compass (GUI) is included
```

### Docker Setup
```bash
# Run MongoDB in Docker
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -v mongodb_data:/data/db \
  mongo:7.0

# Connect to MongoDB
docker exec -it mongodb mongosh -u admin -p password
```

### MongoDB Atlas (Cloud)
```bash
# Free tier available at https://www.mongodb.com/cloud/atlas
# Connection string format:
mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
```

## MongoDB Shell (mongosh)

### Basic Commands

```javascript
// Show databases
show dbs

// Use/create database
use myapp

// Show collections
show collections

// Create collection
db.createCollection('users')

// Insert document
db.users.insertOne({
  username: 'johndoe',
  email: 'john@example.com'
})

// Find documents
db.users.find()
db.users.findOne({username: 'johndoe'})

// Update document
db.users.updateOne(
  {username: 'johndoe'},
  {$set: {email: 'newemail@example.com'}}
)

// Delete document
db.users.deleteOne({username: 'johndoe'})

// Drop collection
db.users.drop()

// Drop database
db.dropDatabase()
```

## Python Integration with PyMongo

### Installation

```bash
pip install pymongo
```

### Basic Connection

```python
from pymongo import MongoClient
from datetime import datetime
import os

# Connect to MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)

# Access database
db = client['myapp']

# Access collection
users = db['users']

# Verify connection
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Failed to connect: {e}")
```

### CRUD Operations

#### Create (Insert)

```python
# Insert one document
user = {
    'username': 'johndoe',
    'email': 'john@example.com',
    'profile': {
        'firstName': 'John',
        'lastName': 'Doe',
        'age': 30
    },
    'interests': ['python', 'databases'],
    'created_at': datetime.utcnow()
}

result = users.insert_one(user)
print(f"Inserted ID: {result.inserted_id}")

# Insert multiple documents
users_list = [
    {'username': 'jane', 'email': 'jane@example.com'},
    {'username': 'bob', 'email': 'bob@example.com'},
    {'username': 'alice', 'email': 'alice@example.com'}
]

result = users.insert_many(users_list)
print(f"Inserted IDs: {result.inserted_ids}")
```

#### Read (Query)

```python
# Find one document
user = users.find_one({'username': 'johndoe'})
print(user)

# Find all documents
all_users = users.find()
for user in all_users:
    print(user['username'])

# Find with filter
adults = users.find({'profile.age': {'$gte': 18}})
for user in adults:
    print(user['username'])

# Find with projection (select specific fields)
users_emails = users.find(
    {},
    {'username': 1, 'email': 1, '_id': 0}  # 1 = include, 0 = exclude
)

# Count documents
count = users.count_documents({'profile.age': {'$gte': 18}})
print(f"Adults: {count}")

# Sort and limit
top_users = users.find().sort('created_at', -1).limit(10)

# Skip and limit (pagination)
page_2 = users.find().skip(10).limit(10)
```

#### Update

```python
# Update one document
result = users.update_one(
    {'username': 'johndoe'},
    {
        '$set': {'email': 'newemail@example.com'},
        '$currentDate': {'updated_at': True}
    }
)
print(f"Modified: {result.modified_count}")

# Update multiple documents
result = users.update_many(
    {'profile.age': {'$lt': 18}},
    {'$set': {'account_type': 'minor'}}
)
print(f"Modified: {result.modified_count}")

# Update operators
users.update_one(
    {'username': 'johndoe'},
    {
        '$inc': {'login_count': 1},              # Increment
        '$push': {'interests': 'mongodb'},        # Add to array
        '$set': {'last_login': datetime.utcnow()}, # Set field
        '$unset': {'temp_field': ''}              # Remove field
    }
)

# Upsert (update or insert)
users.update_one(
    {'username': 'newuser'},
    {'$set': {'email': 'new@example.com'}},
    upsert=True  # Insert if doesn't exist
)

# Replace entire document
users.replace_one(
    {'username': 'johndoe'},
    {
        'username': 'johndoe',
        'email': 'john@example.com',
        'profile': {'firstName': 'John', 'lastName': 'Smith'}
    }
)
```

#### Delete

```python
# Delete one document
result = users.delete_one({'username': 'johndoe'})
print(f"Deleted: {result.deleted_count}")

# Delete multiple documents
result = users.delete_many({'account_type': 'inactive'})
print(f"Deleted: {result.deleted_count}")

# Delete all documents in collection
users.delete_many({})
```

## Query Operators

### Comparison Operators

```python
# $eq: Equal to
users.find({'age': {'$eq': 30}})
# or simply
users.find({'age': 30})

# $ne: Not equal to
users.find({'status': {'$ne': 'inactive'}})

# $gt, $gte: Greater than (or equal)
users.find({'age': {'$gt': 18}})
users.find({'age': {'$gte': 18}})

# $lt, $lte: Less than (or equal)
users.find({'age': {'$lt': 65}})

# $in: In array
users.find({'status': {'$in': ['active', 'pending']}})

# $nin: Not in array
users.find({'status': {'$nin': ['banned', 'deleted']}})
```

### Logical Operators

```python
# $and
users.find({
    '$and': [
        {'age': {'$gte': 18}},
        {'age': {'$lte': 65}}
    ]
})

# $or
users.find({
    '$or': [
        {'status': 'active'},
        {'status': 'pending'}
    ]
})

# $not
users.find({
    'age': {'$not': {'$lt': 18}}
})

# $nor: None of the conditions true
users.find({
    '$nor': [
        {'status': 'banned'},
        {'status': 'deleted'}
    ]
})
```

### Element Operators

```python
# $exists: Field exists
users.find({'phone': {'$exists': True}})

# $type: Field type
users.find({'age': {'$type': 'int'}})
```

### Array Operators

```python
# $all: Array contains all elements
users.find({'interests': {'$all': ['python', 'databases']}})

# $elemMatch: Array element matches condition
users.find({
    'scores': {
        '$elemMatch': {'$gte': 80, '$lte': 100}
    }
})

# $size: Array size
users.find({'interests': {'$size': 3}})
```

### String Operators

```python
# $regex: Regular expression
users.find({'email': {'$regex': '@gmail.com$'}})

# Case-insensitive search
users.find({'username': {'$regex': 'john', '$options': 'i'}})
```

## Indexing

### Why Indexes Matter

Without index:
```
Query: db.users.find({email: 'john@example.com'})
Execution: Scans ALL documents (slow for large collections)
Time: O(n) where n = number of documents
```

With index:
```
Query: db.users.find({email: 'john@example.com'})
Execution: Uses B-tree index (fast lookup)
Time: O(log n) - significantly faster
```

### Creating Indexes

```python
from pymongo import ASCENDING, DESCENDING, TEXT

# Single field index
users.create_index([('email', ASCENDING)], unique=True)

# Compound index (multiple fields)
users.create_index([
    ('country', ASCENDING),
    ('age', DESCENDING)
])

# Text index for full-text search
users.create_index([('bio', TEXT)])

# Geospatial index
places.create_index([('location', '2dsphere')])

# TTL index (auto-delete documents)
sessions.create_index(
    'created_at',
    expireAfterSeconds=3600  # Delete after 1 hour
)

# Partial index (index subset of documents)
users.create_index(
    [('email', ASCENDING)],
    partialFilterExpression={'status': 'active'}
)

# List indexes
for index in users.list_indexes():
    print(index)

# Drop index
users.drop_index('email_1')
```

### Index Best Practices

```python
# ✅ Good: Index frequently queried fields
users.create_index([('email', ASCENDING)])
users.find({'email': 'john@example.com'})  # Uses index

# ✅ Good: Compound index for multiple fields
users.create_index([('country', ASCENDING), ('age', DESCENDING)])
users.find({'country': 'USA', 'age': {'$gte': 18}})  # Uses index

# ❌ Bad: Too many indexes (slows writes)
users.create_index([('field1', ASCENDING)])
users.create_index([('field2', ASCENDING)])
users.create_index([('field3', ASCENDING)])
# ... (20 indexes) - writes become very slow

# Use explain to verify index usage
cursor = users.find({'email': 'john@example.com'})
explain = cursor.explain()
print(explain['executionStats'])
```

## Aggregation Framework

MongoDB's aggregation pipeline processes documents through stages.

### Basic Aggregation

```python
# Match → Group → Sort pipeline
pipeline = [
    # Stage 1: Filter documents
    {
        '$match': {
            'status': 'active',
            'age': {'$gte': 18}
        }
    },
    # Stage 2: Group by country
    {
        '$group': {
            '_id': '$country',
            'count': {'$sum': 1},
            'avg_age': {'$avg': '$age'},
            'total_revenue': {'$sum': '$revenue'}
        }
    },
    # Stage 3: Sort by count
    {
        '$sort': {'count': -1}
    },
    # Stage 4: Limit results
    {
        '$limit': 10
    }
]

results = list(users.aggregate(pipeline))
for result in results:
    print(f"{result['_id']}: {result['count']} users")
```

### Common Aggregation Stages

```python
# $match: Filter documents (like WHERE in SQL)
{'$match': {'status': 'active'}}

# $group: Group documents (like GROUP BY in SQL)
{
    '$group': {
        '_id': '$category',
        'total': {'$sum': '$amount'},
        'count': {'$sum': 1},
        'avg': {'$avg': '$amount'}
    }
}

# $project: Select/reshape fields (like SELECT in SQL)
{
    '$project': {
        'username': 1,
        'email': 1,
        'fullName': {'$concat': ['$firstName', ' ', '$lastName']},
        '_id': 0
    }
}

# $sort: Sort documents (like ORDER BY in SQL)
{'$sort': {'created_at': -1}}  # -1 = descending

# $limit: Limit results
{'$limit': 10}

# $skip: Skip documents (pagination)
{'$skip': 20}

# $unwind: Deconstruct array field
{'$unwind': '$interests'}

# $lookup: Join with another collection (like JOIN in SQL)
{
    '$lookup': {
        'from': 'orders',
        'localField': '_id',
        'foreignField': 'user_id',
        'as': 'user_orders'
    }
}
```

### Complex Aggregation Example

```python
# E-commerce: Top customers by total spend
pipeline = [
    # Join orders with order_items
    {
        '$lookup': {
            'from': 'order_items',
            'localField': '_id',
            'foreignField': 'order_id',
            'as': 'items'
        }
    },
    # Unwind items array
    {'$unwind': '$items'},
    # Group by user, calculate total
    {
        '$group': {
            '_id': '$user_id',
            'total_orders': {'$sum': 1},
            'total_spent': {'$sum': '$items.total'},
            'avg_order_value': {'$avg': '$items.total'},
            'first_order': {'$min': '$created_at'},
            'last_order': {'$max': '$created_at'}
        }
    },
    # Calculate days as customer
    {
        '$project': {
            'total_orders': 1,
            'total_spent': 1,
            'avg_order_value': 1,
            'days_as_customer': {
                '$divide': [
                    {'$subtract': ['$last_order', '$first_order']},
                    86400000  # milliseconds in a day
                ]
            }
        }
    },
    # Sort by total spent
    {'$sort': {'total_spent': -1}},
    # Top 100 customers
    {'$limit': 100}
]

top_customers = list(orders.aggregate(pipeline))
```

## Data Modeling

### Embedded Documents (Denormalization)

**Best for:** Data accessed together, one-to-few relationships

```python
# Blog post with embedded comments
{
    '_id': ObjectId('...'),
    'title': 'Introduction to MongoDB',
    'author': 'John Doe',
    'content': '...',
    'comments': [
        {
            'author': 'Jane Smith',
            'text': 'Great article!',
            'date': ISODate('2024-01-15')
        },
        {
            'author': 'Bob Johnson',
            'text': 'Very helpful',
            'date': ISODate('2024-01-16')
        }
    ],
    'tags': ['mongodb', 'tutorial', 'nosql'],
    'created_at': ISODate('2024-01-01')
}

# Pros:
# ✅ Single query retrieves post and comments
# ✅ Atomic updates
# ✅ Better performance

# Cons:
# ❌ Document size limit (16MB)
# ❌ Duplicate data if comments need separate access
```

### References (Normalization)

**Best for:** Large subdocuments, many-to-many relationships

```python
# Users collection
{
    '_id': ObjectId('507f1f77bcf86cd799439011'),
    'username': 'johndoe',
    'email': 'john@example.com'
}

# Posts collection (references user)
{
    '_id': ObjectId('507f1f77bcf86cd799439012'),
    'title': 'My First Post',
    'author_id': ObjectId('507f1f77bcf86cd799439011'),  # Reference
    'content': '...',
    'created_at': ISODate('2024-01-01')
}

# Query with $lookup (join)
posts.aggregate([
    {
        '$lookup': {
            'from': 'users',
            'localField': 'author_id',
            'foreignField': '_id',
            'as': 'author'
        }
    },
    {
        '$unwind': '$author'  # Convert array to object
    }
])

# Pros:
# ✅ No data duplication
# ✅ Flexible querying
# ✅ No document size issues

# Cons:
# ❌ Requires multiple queries or $lookup
# ❌ More complex queries
```

### Hybrid Approach

```python
# Best of both worlds: Embed frequently accessed data, reference the rest
{
    '_id': ObjectId('...'),
    'title': 'Introduction to MongoDB',
    'author': {
        'id': ObjectId('507f1f77bcf86cd799439011'),
        'username': 'johndoe',  # Embedded for quick access
        'avatar': 'https://...'
    },
    'content': '...',
    'comment_count': 25,
    'latest_comments': [
        {/* Last 5 comments embedded */}
    ],
    'created_at': ISODate('2024-01-01')
}

# Separate comments collection for all comments
{
    '_id': ObjectId('...'),
    'post_id': ObjectId('...'),
    'author': {...},
    'text': '...',
    'created_at': ISODate('...')
}

# Pros:
# ✅ Fast access to common data
# ✅ Full comment history available when needed
# ✅ Balanced approach
```

## Transactions (MongoDB 4.0+)

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['myapp']

# Start a session
with client.start_session() as session:
    # Start transaction
    with session.start_transaction():
        try:
            # Deduct from account A
            db.accounts.update_one(
                {'account_id': 'A'},
                {'$inc': {'balance': -100}},
                session=session
            )

            # Add to account B
            db.accounts.update_one(
                {'account_id': 'B'},
                {'$inc': {'balance': 100}},
                session=session
            )

            # If we get here, commit automatically
            print("Transaction succeeded")

        except Exception as e:
            # Transaction automatically aborted on exception
            print(f"Transaction failed: {e}")
            raise

# Transaction guarantees:
# - Atomicity: All or nothing
# - Consistency: Valid state maintained
# - Isolation: Concurrent transactions don't interfere
# - Durability: Committed changes persist
```

## Replication

MongoDB uses replica sets for high availability.

```
Primary Node (Read/Write)
    ├─→ Secondary Node 1 (Read-only)
    ├─→ Secondary Node 2 (Read-only)
    └─→ Secondary Node 3 (Read-only)

If Primary fails → Automatic election → Secondary becomes Primary
```

### Setup Replica Set

```javascript
// Start MongoDB instances with replica set name
// mongod --replSet rs0 --port 27017
// mongod --replSet rs0 --port 27018
// mongod --replSet rs0 --port 27019

// Connect to one instance and initiate
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "localhost:27017" },
    { _id: 1, host: "localhost:27018" },
    { _id: 2, host: "localhost:27019" }
  ]
})

// Check status
rs.status()
```

### Python with Replica Set

```python
from pymongo import MongoClient, ReadPreference

# Connect to replica set
client = MongoClient(
    'mongodb://localhost:27017,localhost:27018,localhost:27019/',
    replicaSet='rs0'
)

db = client['myapp']

# Write to primary (default)
db.users.insert_one({'username': 'john'})

# Read from secondaries (distribute load)
users = db.users.find().read_preference(ReadPreference.SECONDARY)

# Read from nearest (lowest latency)
users = db.users.find().read_preference(ReadPreference.NEAREST)
```

## Sharding

Horizontal scaling by distributing data across multiple servers.

```
Router (mongos)
    ├─→ Shard 1 (users A-M)
    ├─→ Shard 2 (users N-Z)
    └─→ Config Servers (metadata)
```

### Enable Sharding

```javascript
// Enable sharding for database
sh.enableSharding("myapp")

// Shard collection by key
sh.shardCollection(
    "myapp.users",
    { "username": "hashed" }  // Shard key
)

// Check shard distribution
db.users.getShardDistribution()
```

## Best Practices

### 1. Schema Design
- ✅ Design for your access patterns
- ✅ Embed data accessed together
- ✅ Use references for large subdocuments
- ✅ Avoid unbounded arrays

### 2. Indexing
- ✅ Index frequently queried fields
- ✅ Use compound indexes for multiple fields
- ✅ Monitor index usage with explain()
- ❌ Don't over-index (slows writes)

### 3. Queries
- ✅ Use projection to limit returned fields
- ✅ Use limit() to cap results
- ✅ Leverage aggregation framework
- ❌ Avoid large skip() values (use range queries)

### 4. Performance
- ✅ Use connection pooling
- ✅ Batch operations when possible
- ✅ Monitor slow queries
- ✅ Set appropriate write concerns

### 5. Security
- ✅ Enable authentication
- ✅ Use role-based access control
- ✅ Encrypt connections (TLS)
- ✅ Regular backups

## Summary

MongoDB excels at:
- **Flexible schemas** for evolving data models
- **Nested documents** for hierarchical data
- **Horizontal scaling** for growing applications
- **Rich queries** with aggregation framework
- **High availability** with replica sets

Perfect for:
- Content management systems
- Product catalogs
- User profiles
- Real-time analytics
- Mobile applications

## Next Steps

- [Complete MongoDB Example](../../examples/python/mongodb_example.py)
- [Cassandra Guide](../cassandra/README.md)
- [Redis Guide](../redis/README.md)
- [Performance Optimization](../../09-performance/README.md)

---

[← Back to NoSQL](../README.md) | [Next: Cassandra →](../cassandra/README.md)
