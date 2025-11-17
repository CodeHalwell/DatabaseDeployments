# Redis: In-Memory Data Structure Store

## Overview

Redis (Remote Dictionary Server) is an in-memory data structure store used as a database, cache, message broker, and streaming engine. It provides sub-millisecond response times and is known for exceptional performance.

## What is Redis?

**Redis** is an open-source, in-memory key-value data store that supports multiple data structures:
- **Strings** - Simple key-value pairs
- **Hashes** - Field-value pairs (like objects)
- **Lists** - Ordered collections
- **Sets** - Unordered unique collections
- **Sorted Sets** - Sets with scores for ranking
- **Streams** - Log-like data structures
- **Bitmaps, HyperLogLogs, Geospatial indexes**

### Key Features

- ⚡ **Blazing Fast**: All data in memory, sub-millisecond latency
- 🔄 **Persistence Options**: RDB snapshots and AOF (Append-Only File)
- 📡 **Pub/Sub**: Real-time messaging
- 🔁 **Replication**: Master-replica for high availability
- 📊 **Transactions**: MULTI/EXEC for atomic operations
- 🌐 **Cluster Mode**: Horizontal scaling

## When to Use Redis

### Ideal Use Cases

✅ **Caching**
- Database query results
- API responses
- Session data
- Computed values

✅ **Session Storage**
- Web session management
- User authentication tokens
- Shopping carts

✅ **Real-Time Analytics**
- Page view counters
- Unique visitor tracking
- Real-time leaderboards
- Rate limiting

✅ **Message Queues**
- Task queues
- Job scheduling
- Event streaming
- Pub/Sub messaging

✅ **Leaderboards**
- Gaming scoreboards
- Social media trends
- Real-time rankings

✅ **Geospatial**
- Location-based services
- Nearby searches
- Distance calculations

### When NOT to Use Redis

❌ **Large Dataset Storage** (use disk-based databases)
- Redis is limited by RAM size
- Expensive for terabyte-scale data

❌ **Complex Queries** (use SQL or document databases)
- No JOIN operations
- Limited query capabilities

❌ **Primary Database** (use as cache/supplement)
- Data volatility (unless persistence configured)
- Better as cache layer

## Installation and Setup

### Local Installation

**macOS:**
```bash
# Using Homebrew
brew install redis

# Start Redis
brew services start redis

# Or run manually
redis-server
```

**Ubuntu:**
```bash
# Install Redis
sudo apt update
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Check status
sudo systemctl status redis-server
```

**Windows:**
```powershell
# Using WSL or download from GitHub
# https://github.com/microsoftarchive/redis/releases

# Or use Docker (recommended)
docker run -d --name redis -p 6379:6379 redis:7
```

### Docker Setup

```bash
# Basic Redis container
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7

# With persistence
docker run -d \
  --name redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:7 redis-server --appendonly yes

# With password
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7 redis-server --requirepass mypassword

# Redis with Redis Insight (GUI)
docker run -d \
  --name redisinsight \
  -p 8001:8001 \
  redis/redisinsight:latest
```

### Redis Cloud
- **Redis Enterprise Cloud**: https://redis.com/try-free/
- **AWS ElastiCache**: Managed Redis on AWS
- **Azure Cache for Redis**: Managed Redis on Azure
- **Google Cloud Memorystore**: Managed Redis on GCP

## Redis CLI

### Basic Commands

```bash
# Connect to Redis
redis-cli

# With password
redis-cli -a mypassword

# Ping server
ping
# PONG

# Set key
SET mykey "Hello"

# Get key
GET mykey
# "Hello"

# Check if key exists
EXISTS mykey
# (integer) 1

# Delete key
DEL mykey
# (integer) 1

# Set with expiration (seconds)
SETEX session:123 3600 "user_data"

# Get TTL (time to live)
TTL session:123
# (integer) 3599

# Get all keys (use sparingly in production!)
KEYS *

# Scan keys (production-safe)
SCAN 0 MATCH user:* COUNT 100

# Flush all data (be careful!)
FLUSHALL
```

## Python Integration with redis-py

### Installation

```bash
pip install redis
```

### Basic Connection

```python
import redis
import json
from datetime import timedelta

# Connect to Redis
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True  # Return strings instead of bytes
)

# With password
r = redis.Redis(
    host='localhost',
    port=6379,
    password='mypassword',
    db=0,
    decode_responses=True
)

# Connection pool (recommended for production)
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=10,
    decode_responses=True
)
r = redis.Redis(connection_pool=pool)

# Test connection
try:
    r.ping()
    print("Connected to Redis!")
except redis.ConnectionError:
    print("Failed to connect to Redis")
```

## Data Structures and Operations

### 1. Strings (Simple Key-Value)

```python
# Set value
r.set('user:1000:name', 'John Doe')

# Get value
name = r.get('user:1000:name')
print(name)  # 'John Doe'

# Set with expiration
r.setex('verification:abc123', 300, 'email_code')  # 5 minutes

# Set if not exists
r.setnx('config:lock', 'process_id')

# Increment (atomic)
r.set('page:views', 0)
r.incr('page:views')  # 1
r.incr('page:views')  # 2
r.incrby('page:views', 10)  # 12

# Decrement
r.decr('inventory:item:500')  # Atomic decrement

# Get and set
old_value = r.getset('counter', 0)

# Multiple operations
r.mset({
    'user:1:name': 'John',
    'user:2:name': 'Jane',
    'user:3:name': 'Bob'
})

values = r.mget('user:1:name', 'user:2:name', 'user:3:name')
print(values)  # ['John', 'Jane', 'Bob']

# Store complex data as JSON
user_data = {
    'username': 'johndoe',
    'email': 'john@example.com',
    'age': 30
}
r.set('user:1000', json.dumps(user_data))

# Retrieve and parse JSON
data = json.loads(r.get('user:1000'))
```

### 2. Hashes (Field-Value Pairs)

```python
# Set hash fields
r.hset('user:1000', 'username', 'johndoe')
r.hset('user:1000', 'email', 'john@example.com')
r.hset('user:1000', 'age', 30)

# Set multiple fields at once
r.hset('user:1000', mapping={
    'username': 'johndoe',
    'email': 'john@example.com',
    'age': 30,
    'city': 'New York'
})

# Get single field
username = r.hget('user:1000', 'username')

# Get multiple fields
fields = r.hmget('user:1000', 'username', 'email')

# Get all fields
user = r.hgetall('user:1000')
print(user)
# {'username': 'johndoe', 'email': 'john@example.com', 'age': '30', 'city': 'New York'}

# Check if field exists
exists = r.hexists('user:1000', 'username')

# Delete field
r.hdel('user:1000', 'city')

# Increment hash field
r.hincrby('user:1000', 'login_count', 1)

# Get all field names
fields = r.hkeys('user:1000')

# Get all values
values = r.hvals('user:1000')

# Get number of fields
count = r.hlen('user:1000')
```

### 3. Lists (Ordered Collections)

```python
# Push to left (beginning)
r.lpush('notifications:user:1000', 'New message from Jane')
r.lpush('notifications:user:1000', 'Order shipped')

# Push to right (end)
r.rpush('queue:tasks', 'task1')
r.rpush('queue:tasks', 'task2')
r.rpush('queue:tasks', 'task3')

# Get list length
length = r.llen('queue:tasks')

# Get range of elements
tasks = r.lrange('queue:tasks', 0, -1)  # All elements
recent = r.lrange('notifications:user:1000', 0, 9)  # First 10

# Pop from left (FIFO queue)
task = r.lpop('queue:tasks')

# Pop from right (LIFO stack)
task = r.rpop('queue:tasks')

# Blocking pop (wait for element)
task = r.blpop('queue:tasks', timeout=5)  # Wait up to 5 seconds

# Get element by index
r.lindex('notifications:user:1000', 0)

# Trim list (keep only range)
r.ltrim('recent:articles', 0, 99)  # Keep only 100 most recent

# Remove elements
r.lrem('queue:tasks', 1, 'task2')  # Remove first occurrence

# Use case: Activity feed
def add_activity(user_id, activity):
    """Add activity to feed, keep only 100 most recent"""
    key = f'feed:user:{user_id}'
    r.lpush(key, json.dumps(activity))
    r.ltrim(key, 0, 99)  # Keep only 100 items

def get_feed(user_id, count=20):
    """Get recent activities"""
    key = f'feed:user:{user_id}'
    activities = r.lrange(key, 0, count - 1)
    return [json.loads(a) for a in activities]
```

### 4. Sets (Unordered Unique Collections)

```python
# Add members
r.sadd('user:1000:interests', 'python')
r.sadd('user:1000:interests', 'databases', 'cloud')

# Add multiple
r.sadd('tags:article:1', 'python', 'tutorial', 'beginner')

# Check membership
is_member = r.sismember('user:1000:interests', 'python')  # True

# Get all members
interests = r.smembers('user:1000:interests')
print(interests)  # {'python', 'databases', 'cloud'}

# Remove member
r.srem('user:1000:interests', 'databases')

# Pop random member
random = r.spop('user:1000:interests')

# Get random member (without removing)
random = r.srandmember('user:1000:interests')

# Get count
count = r.scard('user:1000:interests')

# Set operations
r.sadd('python:developers', 'user:1', 'user:2', 'user:3')
r.sadd('javascript:developers', 'user:2', 'user:3', 'user:4')

# Union (OR)
all_devs = r.sunion('python:developers', 'javascript:developers')
# {'user:1', 'user:2', 'user:3', 'user:4'}

# Intersection (AND)
both = r.sinter('python:developers', 'javascript:developers')
# {'user:2', 'user:3'}

# Difference (A - B)
only_python = r.sdiff('python:developers', 'javascript:developers')
# {'user:1'}

# Use case: Tagging system
def add_tag(item_id, tag):
    """Add tag to item"""
    r.sadd(f'item:{item_id}:tags', tag)
    r.sadd(f'tag:{tag}:items', item_id)

def get_items_by_tags(tags):
    """Find items with ALL specified tags (intersection)"""
    keys = [f'tag:{tag}:items' for tag in tags]
    return r.sinter(*keys)
```

### 5. Sorted Sets (Scored Collections)

```python
# Add members with scores
r.zadd('leaderboard', {
    'player1': 1500,
    'player2': 2000,
    'player3': 1800,
    'player4': 2200
})

# Add with single member
r.zadd('leaderboard', {'player5': 1900})

# Get score
score = r.zscore('leaderboard', 'player1')  # 1500.0

# Increment score
r.zincrby('leaderboard', 100, 'player1')  # 1600

# Get rank (0-based)
rank = r.zrank('leaderboard', 'player1')  # Position from lowest
rev_rank = r.zrevrank('leaderboard', 'player1')  # Position from highest

# Get range (by rank)
top_players = r.zrevrange('leaderboard', 0, 9, withscores=True)
# [('player4', 2200.0), ('player2', 2000.0), ...]

# Get range (by score)
mid_players = r.zrangebyscore('leaderboard', 1500, 2000, withscores=True)

# Count in range
count = r.zcount('leaderboard', 1500, 2000)

# Remove member
r.zrem('leaderboard', 'player1')

# Remove by rank
r.zremrangebyrank('leaderboard', 0, 2)  # Remove bottom 3

# Remove by score
r.zremrangebyscore('leaderboard', 0, 1000)  # Remove scores < 1000

# Get cardinality (count)
count = r.zcard('leaderboard')

# Use case: Real-time leaderboard
def update_score(player_id, points):
    """Update player score"""
    r.zincrby('leaderboard:global', points, player_id)

    # Also update daily leaderboard with expiration
    today = datetime.now().strftime('%Y-%m-%d')
    r.zincrby(f'leaderboard:daily:{today}', points, player_id)
    r.expire(f'leaderboard:daily:{today}', 86400 * 7)  # Keep 7 days

def get_leaderboard(limit=10):
    """Get top players"""
    players = r.zrevrange('leaderboard:global', 0, limit - 1, withscores=True)
    return [{'player': p, 'score': int(s)} for p, s in players]

def get_player_rank(player_id):
    """Get player's global rank"""
    rank = r.zrevrank('leaderboard:global', player_id)
    score = r.zscore('leaderboard:global', player_id)
    return {'rank': rank + 1 if rank is not None else None, 'score': score}

# Use case: Trending posts (time-decay scoring)
def add_post(post_id, votes, timestamp):
    """Add post with time-decayed score"""
    # Score decreases over time
    age_hours = (time.time() - timestamp) / 3600
    score = votes / (age_hours + 2) ** 1.5
    r.zadd('trending:posts', {post_id: score})

def get_trending():
    """Get trending posts"""
    return r.zrevrange('trending:posts', 0, 19)  # Top 20
```

## Caching Patterns

### 1. Cache-Aside (Lazy Loading)

```python
def get_user(user_id):
    """Cache-aside pattern"""
    cache_key = f'user:{user_id}'

    # Try cache first
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss - query database
    user = database.query('SELECT * FROM users WHERE id = ?', user_id)

    # Store in cache
    r.setex(cache_key, 3600, json.dumps(user))  # 1 hour TTL

    return user
```

### 2. Write-Through Cache

```python
def update_user(user_id, data):
    """Write-through cache pattern"""
    cache_key = f'user:{user_id}'

    # Update database
    database.execute('UPDATE users SET ... WHERE id = ?', user_id, data)

    # Update cache immediately
    r.setex(cache_key, 3600, json.dumps(data))

    return data
```

### 3. Cache Invalidation

```python
def delete_user(user_id):
    """Invalidate cache on delete"""
    cache_key = f'user:{user_id}'

    # Delete from database
    database.execute('DELETE FROM users WHERE id = ?', user_id)

    # Invalidate cache
    r.delete(cache_key)
```

### 4. Memoization Decorator

```python
import functools
import hashlib

def redis_cache(expiration=3600):
    """Decorator to cache function results in Redis"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = f"{func.__name__}:{args}:{kwargs}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()

            # Try cache
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            r.setex(cache_key, expiration, json.dumps(result))

            return result
        return wrapper
    return decorator

@redis_cache(expiration=300)  # Cache for 5 minutes
def expensive_computation(n):
    """Expensive function that gets cached"""
    import time
    time.sleep(2)  # Simulate slow operation
    return sum(range(n))

# First call: slow (2+ seconds)
result = expensive_computation(1000000)

# Subsequent calls: fast (milliseconds)
result = expensive_computation(1000000)
```

## Session Management

```python
import uuid
from datetime import datetime, timedelta

class SessionManager:
    """Redis-based session management"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.session_ttl = 3600  # 1 hour

    def create_session(self, user_id, user_data):
        """Create new session"""
        session_id = str(uuid.uuid4())
        session_key = f'session:{session_id}'

        session_data = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            **user_data
        }

        # Store session with expiration
        self.redis.hset(session_key, mapping=session_data)
        self.redis.expire(session_key, self.session_ttl)

        # Track active sessions for user
        self.redis.sadd(f'user:{user_id}:sessions', session_id)

        return session_id

    def get_session(self, session_id):
        """Retrieve session data"""
        session_key = f'session:{session_id}'

        # Get session data
        data = self.redis.hgetall(session_key)

        if data:
            # Refresh TTL on access
            self.redis.expire(session_key, self.session_ttl)
            return data

        return None

    def update_session(self, session_id, updates):
        """Update session data"""
        session_key = f'session:{session_id}'

        if self.redis.exists(session_key):
            self.redis.hset(session_key, mapping=updates)
            self.redis.expire(session_key, self.session_ttl)
            return True

        return False

    def destroy_session(self, session_id):
        """Destroy session"""
        session_key = f'session:{session_id}'

        # Get user_id before deletion
        user_id = self.redis.hget(session_key, 'user_id')

        # Delete session
        self.redis.delete(session_key)

        # Remove from user's active sessions
        if user_id:
            self.redis.srem(f'user:{user_id}:sessions', session_id)

    def destroy_user_sessions(self, user_id):
        """Destroy all sessions for a user"""
        sessions = self.redis.smembers(f'user:{user_id}:sessions')

        for session_id in sessions:
            self.redis.delete(f'session:{session_id}')

        self.redis.delete(f'user:{user_id}:sessions')

# Usage
session_mgr = SessionManager(r)

# Create session
session_id = session_mgr.create_session(
    user_id=1000,
    user_data={'username': 'johndoe', 'role': 'admin'}
)

# Get session
session = session_mgr.get_session(session_id)

# Update session
session_mgr.update_session(session_id, {'last_activity': datetime.now().isoformat()})

# Destroy session
session_mgr.destroy_session(session_id)
```

## Rate Limiting

```python
import time

class RateLimiter:
    """Redis-based rate limiter"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def is_allowed(self, key, max_requests, window_seconds):
        """
        Check if request is allowed

        Args:
            key: Identifier (user_id, IP, API key)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            (allowed, remaining, reset_time)
        """
        current_time = int(time.time())
        window_start = current_time - window_seconds

        # Redis key
        rate_key = f'rate_limit:{key}'

        # Remove old entries
        self.redis.zremrangebyscore(rate_key, 0, window_start)

        # Count requests in current window
        request_count = self.redis.zcard(rate_key)

        if request_count < max_requests:
            # Add current request
            self.redis.zadd(rate_key, {str(current_time): current_time})
            self.redis.expire(rate_key, window_seconds)

            remaining = max_requests - request_count - 1
            return True, remaining, current_time + window_seconds
        else:
            # Rate limit exceeded
            remaining = 0
            # Get oldest request timestamp
            oldest = self.redis.zrange(rate_key, 0, 0, withscores=True)
            reset_time = int(oldest[0][1]) + window_seconds if oldest else current_time + window_seconds

            return False, remaining, reset_time

# Usage
rate_limiter = RateLimiter(r)

# API endpoint with rate limiting
def api_endpoint(user_id):
    # Allow 100 requests per hour
    allowed, remaining, reset_time = rate_limiter.is_allowed(
        key=f'user:{user_id}',
        max_requests=100,
        window_seconds=3600
    )

    if not allowed:
        return {
            'error': 'Rate limit exceeded',
            'retry_after': reset_time - int(time.time())
        }, 429

    # Process request
    return {
        'data': '...',
        'rate_limit': {
            'remaining': remaining,
            'reset': reset_time
        }
    }, 200
```

## Pub/Sub Messaging

```python
import threading

# Publisher
def publish_event(channel, message):
    """Publish message to channel"""
    r.publish(channel, json.dumps(message))

# Subscriber
def subscribe_to_events(channels):
    """Subscribe to channels and handle messages"""
    pubsub = r.pubsub()
    pubsub.subscribe(*channels)

    print(f"Subscribed to {channels}")

    for message in pubsub.listen():
        if message['type'] == 'message':
            channel = message['channel']
            data = json.loads(message['data'])

            # Handle message
            print(f"Received on {channel}: {data}")
            handle_event(channel, data)

def handle_event(channel, data):
    """Handle received event"""
    if channel == 'orders':
        print(f"New order: {data}")
    elif channel == 'notifications':
        print(f"Notification: {data}")

# Run subscriber in separate thread
subscriber_thread = threading.Thread(
    target=subscribe_to_events,
    args=(['orders', 'notifications'],),
    daemon=True
)
subscriber_thread.start()

# Publish events
publish_event('orders', {'order_id': 123, 'total': 150.00})
publish_event('notifications', {'user_id': 1000, 'message': 'Order shipped'})

# Pattern subscription
pubsub = r.pubsub()
pubsub.psubscribe('user:*')  # Subscribe to all user channels
```

## Transactions

```python
# Pipeline (not atomic, but batched)
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.incr('counter')
results = pipe.execute()

# MULTI/EXEC transaction (atomic)
pipe = r.pipeline(transaction=True)
pipe.multi()
pipe.decrby('inventory:item:500', 1)
pipe.incrby('cart:user:1000:item:500', 1)
results = pipe.execute()

# WATCH for optimistic locking
def transfer_credits(from_user, to_user, amount):
    """Transfer credits between users atomically"""
    with r.pipeline() as pipe:
        while True:
            try:
                # Watch keys
                pipe.watch(f'credits:{from_user}', f'credits:{to_user}')

                # Check balance
                balance = int(pipe.get(f'credits:{from_user}') or 0)

                if balance < amount:
                    pipe.unwatch()
                    return False, "Insufficient credits"

                # Execute transaction
                pipe.multi()
                pipe.decrby(f'credits:{from_user}', amount)
                pipe.incrby(f'credits:{to_user}', amount)
                pipe.execute()

                return True, "Transfer successful"

            except redis.WatchError:
                # Another client modified the keys, retry
                continue
```

## Persistence

### RDB (Snapshots)

```bash
# redis.conf
save 900 1    # Save if at least 1 key changed in 900 seconds
save 300 10   # Save if at least 10 keys changed in 300 seconds
save 60 10000 # Save if at least 10000 keys changed in 60 seconds

# Manual save
redis-cli SAVE    # Blocking
redis-cli BGSAVE  # Background
```

### AOF (Append-Only File)

```bash
# redis.conf
appendonly yes
appendfsync everysec  # fsync every second (default)
# appendfsync always  # fsync every write (slow, safest)
# appendfsync no      # Let OS decide (fast, less safe)
```

## Best Practices

### 1. Key Naming Convention
```python
# ✅ Good: Hierarchical, descriptive
'user:1000:profile'
'session:abc123'
'cache:product:500'
'leaderboard:game:global'

# ❌ Bad: Unclear, flat structure
'u1000'
'data123'
'x'
```

### 2. Set Expiration
```python
# ✅ Good: Always set TTL for temporary data
r.setex('session:abc123', 3600, data)
r.expire('cache:page:home', 300)

# ❌ Bad: Data never expires, memory leak
r.set('temp:data', value)  # No expiration!
```

### 3. Use Pipelining
```python
# ✅ Good: Batch operations
pipe = r.pipeline()
for i in range(1000):
    pipe.set(f'key:{i}', f'value:{i}')
pipe.execute()

# ❌ Bad: Individual network calls
for i in range(1000):
    r.set(f'key:{i}', f'value:{i}')  # 1000 round trips!
```

### 4. Connection Pooling
```python
# ✅ Good: Reuse connections
pool = redis.ConnectionPool(host='localhost', port=6379, max_connections=10)
r = redis.Redis(connection_pool=pool)

# ❌ Bad: New connection each time
r = redis.Redis(host='localhost', port=6379)  # Don't do this in loops!
```

### 5. Monitor Memory
```python
# Check memory usage
info = r.info('memory')
print(f"Used memory: {info['used_memory_human']}")
print(f"Max memory: {info['maxmemory_human']}")

# Set memory policy
# redis.conf: maxmemory-policy allkeys-lru
# Options: noeviction, allkeys-lru, volatile-lru, etc.
```

## Summary

Redis excels at:
- **High-performance caching** (sub-millisecond latency)
- **Session management** (distributed sessions)
- **Real-time analytics** (counters, leaderboards)
- **Message queues** (Pub/Sub, streams)
- **Rate limiting** (sorted sets with time windows)

Perfect for:
- Caching database queries and API responses
- Web session storage
- Real-time leaderboards and counters
- Job queues and task scheduling
- Real-time messaging

## Next Steps

- [Complete Redis Example](../../examples/python/redis_example.py)
- [DynamoDB Guide](../dynamodb/README.md)
- [Performance Optimization](../../09-performance/README.md)
- [Caching Strategies](../../09-performance/caching.md)

---

[← Back to NoSQL](../README.md) | [Next: DynamoDB →](../dynamodb/README.md)
