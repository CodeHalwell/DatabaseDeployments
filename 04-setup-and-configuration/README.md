# Part 4: Setup and Development Environment

## Overview

Setting up a proper development environment is crucial for productive database work. This section covers local installation, Docker setups, environment management, and essential tools for database development.

## What You'll Learn

- Local database installation (PostgreSQL, MySQL, MongoDB, Redis)
- Docker-based development environments
- Environment variables and configuration management
- Database GUI tools and administration
- Development best practices
- Connection string management
- Backup and restore procedures

## Quick Start: Docker Compose Setup

The fastest way to get started with multiple databases:

### Complete Development Stack

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:15
    container_name: dev-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: dev_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MySQL
  mysql:
    image: mysql:8.0
    container_name: dev-mysql
    environment:
      MYSQL_ROOT_PASSWORD: mysql
      MYSQL_DATABASE: dev_db
      MYSQL_USER: developer
      MYSQL_PASSWORD: developer
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MongoDB
  mongodb:
    image: mongo:7.0
    container_name: dev-mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    container_name: dev-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # pgAdmin (PostgreSQL GUI)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: dev-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    depends_on:
      - postgres

  # Mongo Express (MongoDB GUI)
  mongo-express:
    image: mongo-express:latest
    container_name: dev-mongo-express
    environment:
      ME_CONFIG_MONGODB_ADMINUSERNAME: admin
      ME_CONFIG_MONGODB_ADMINPASSWORD: admin
      ME_CONFIG_MONGODB_URL: mongodb://admin:admin@mongodb:27017/
    ports:
      - "8081:8081"
    depends_on:
      - mongodb

  # Redis Insight (Redis GUI)
  redis-insight:
    image: redis/redisinsight:latest
    container_name: dev-redis-insight
    ports:
      - "5540:5540"
    volumes:
      - redis-insight_data:/db
    depends_on:
      - redis

volumes:
  postgres_data:
  mysql_data:
  mongodb_data:
  redis_data:
  pgadmin_data:
  redis-insight_data:

networks:
  default:
    name: dev-network
```

### Starting the Development Environment

```bash
# Start all databases
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres

# Stop all databases
docker-compose down

# Stop and remove volumes (WARNING: deletes data!)
docker-compose down -v
```

### Accessing the Databases

```bash
# PostgreSQL
psql -h localhost -U postgres -d dev_db
# Password: postgres

# MySQL
mysql -h localhost -u developer -p
# Password: developer

# MongoDB
mongosh mongodb://admin:admin@localhost:27017

# Redis
redis-cli -h localhost -p 6379
```

### GUI Access

- **pgAdmin** (PostgreSQL): http://localhost:5050
  - Email: admin@example.com
  - Password: admin

- **Mongo Express** (MongoDB): http://localhost:8081
  - Username: admin
  - Password: admin

- **Redis Insight** (Redis): http://localhost:5540

## Local Installation

### PostgreSQL

**macOS:**
```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb myapp_dev

# Connect
psql myapp_dev
```

**Ubuntu/Debian:**
```bash
# Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Install
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Switch to postgres user and create database
sudo -u postgres createdb myapp_dev
sudo -u postgres createuser --interactive
```

**Windows:**
```powershell
# Download from https://www.postgresql.org/download/windows/
# Run installer and follow prompts
# Add to PATH: C:\Program Files\PostgreSQL\15\bin

# Create database via pgAdmin or command line
psql -U postgres
CREATE DATABASE myapp_dev;
```

### MySQL

**macOS:**
```bash
# Using Homebrew
brew install mysql
brew services start mysql

# Secure installation
mysql_secure_installation

# Connect
mysql -u root -p
```

**Ubuntu/Debian:**
```bash
# Install
sudo apt update
sudo apt install mysql-server

# Secure installation
sudo mysql_secure_installation

# Start service
sudo systemctl start mysql
sudo systemctl enable mysql

# Connect
sudo mysql
```

**Windows:**
```powershell
# Download MySQL Installer from https://dev.mysql.com/downloads/installer/
# Run installer and select "Developer Default"
# Follow setup wizard

# Connect
mysql -u root -p
```

### MongoDB

**macOS:**
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Connect
mongosh
```

**Ubuntu/Debian:**
```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Create list file
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install
sudo apt update
sudo apt install -y mongodb-org

# Start service
sudo systemctl start mongod
sudo systemctl enable mongod

# Connect
mongosh
```

**Windows:**
```powershell
# Download MongoDB Community Server from https://www.mongodb.com/try/download/community
# Run installer (includes MongoDB Compass GUI)
# Add to PATH: C:\Program Files\MongoDB\Server\7.0\bin

# Connect
mongosh
```

### Redis

**macOS:**
```bash
# Using Homebrew
brew install redis
brew services start redis

# Connect
redis-cli
```

**Ubuntu/Debian:**
```bash
# Install
sudo apt update
sudo apt install redis-server

# Configure to start on boot
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Connect
redis-cli
```

**Windows:**
```powershell
# Redis doesn't officially support Windows
# Use WSL (Windows Subsystem for Linux) or Docker

# WSL Ubuntu
wsl --install -d Ubuntu
# Then follow Ubuntu instructions

# Or use Docker
docker run -d --name redis -p 6379:6379 redis:7
```

## Environment Configuration

### .env File Management

Create `.env` file in your project root:

```bash
# .env
# Database connections

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=myapp_dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/myapp_dev

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=myapp_dev
MYSQL_USER=developer
MYSQL_PASSWORD=developer

# MongoDB
MONGO_URI=mongodb://localhost:27017/myapp_dev
# For authenticated MongoDB:
# MONGO_URI=mongodb://username:password@localhost:27017/myapp_dev

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug
```

### Using .env in Python

```python
# Install python-dotenv
# pip install python-dotenv

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Access variables
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

# Or use DATABASE_URL directly
DATABASE_URL = os.getenv('DATABASE_URL')

# MongoDB
MONGO_URI = os.getenv('MONGO_URI')

# Redis
REDIS_URL = os.getenv('REDIS_URL')
```

### Using .env in Node.js

```javascript
// Install dotenv
// npm install dotenv

require('dotenv').config();

// Access variables
const config = {
  postgres: {
    host: process.env.POSTGRES_HOST || 'localhost',
    port: parseInt(process.env.POSTGRES_PORT) || 5432,
    database: process.env.POSTGRES_DB,
    user: process.env.POSTGRES_USER,
    password: process.env.POSTGRES_PASSWORD
  },
  mongodb: {
    uri: process.env.MONGO_URI
  },
  redis: {
    url: process.env.REDIS_URL
  }
};

module.exports = config;
```

### .gitignore for Secrets

```bash
# .gitignore
# Never commit sensitive data!

.env
.env.local
.env.*.local
secrets/
*.pem
*.key
credentials.json
```

### Environment-Specific Configuration

```python
# config.py
import os

class Config:
    """Base configuration"""
    DATABASE_URL = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL')

class DevelopmentConfig(Config):
    """Development environment"""
    DEBUG = True
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/myapp_dev')

class ProductionConfig(Config):
    """Production environment"""
    DEBUG = False
    DATABASE_URL = os.getenv('DATABASE_URL')  # Must be set in production

class TestingConfig(Config):
    """Testing environment"""
    TESTING = True
    DATABASE_URL = 'postgresql://localhost/myapp_test'

# Select configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config():
    env = os.getenv('ENVIRONMENT', 'development')
    return config[env]
```

## Database GUI Tools

### PostgreSQL Tools

#### pgAdmin
- **Website**: https://www.pgadmin.org/
- **Features**: Query tool, visual explain, backup/restore, monitoring
- **Platform**: Windows, macOS, Linux, Web

#### DBeaver
- **Website**: https://dbeaver.io/
- **Features**: Universal database tool, supports multiple databases
- **Platform**: Windows, macOS, Linux

#### TablePlus
- **Website**: https://tableplus.com/
- **Features**: Modern, fast interface, native apps
- **Platform**: macOS, Windows, Linux, iOS

### MongoDB Tools

#### MongoDB Compass
- **Website**: https://www.mongodb.com/products/compass
- **Features**: Visual query builder, aggregation pipeline builder, performance insights
- **Platform**: Windows, macOS, Linux

#### Studio 3T
- **Website**: https://studio3t.com/
- **Features**: Advanced query builder, SQL migration, import/export
- **Platform**: Windows, macOS, Linux

### Redis Tools

#### Redis Insight
- **Website**: https://redis.com/redis-enterprise/redis-insight/
- **Features**: Real-time monitoring, memory analysis, CLI interface
- **Platform**: Windows, macOS, Linux, Web

#### RedisInsight
- **Website**: https://redis.io/insight/
- **Features**: Browser-based GUI, memory profiler
- **Platform**: Desktop and web

### Universal Tools

#### DBeaver
- Supports PostgreSQL, MySQL, MongoDB (via plugin), SQLite, and more
- Free and open-source
- Cross-platform

#### DataGrip (JetBrains)
- Professional database IDE
- Supports virtually all databases
- Paid (free for students)

## Connection String Formats

### PostgreSQL
```
# Basic
postgresql://username:password@hostname:port/database

# With options
postgresql://user:pass@localhost:5432/mydb?sslmode=require

# Multiple hosts (HA)
postgresql://user:pass@host1:5432,host2:5432/mydb
```

### MySQL
```
# Basic
mysql://username:password@hostname:port/database

# With options
mysql://user:pass@localhost:3306/mydb?charset=utf8mb4
```

### MongoDB
```
# Basic
mongodb://username:password@hostname:port/database

# With replica set
mongodb://user:pass@host1:27017,host2:27017,host3:27017/mydb?replicaSet=rs0

# MongoDB Atlas
mongodb+srv://username:password@cluster.mongodb.net/database
```

### Redis
```
# Basic
redis://hostname:port/database

# With password
redis://:password@hostname:port/database

# Redis Sentinel
redis-sentinel://host1:26379,host2:26379/mymaster
```

## Development Best Practices

### 1. Use Separate Databases per Environment

```
myapp_development  # Local development
myapp_test         # Automated tests
myapp_staging      # Pre-production
myapp_production   # Production
```

### 2. Database Migrations

```python
# Use migration tools instead of manual schema changes

# Alembic (Python)
alembic revision --autogenerate -m "Add users table"
alembic upgrade head

# Django
python manage.py makemigrations
python manage.py migrate

# Flyway (Java)
flyway migrate

# Liquibase (Multi-platform)
liquibase update
```

### 3. Seed Data for Development

```python
# seed.py
from database import db, User, Product

def seed_database():
    """Populate database with sample data"""

    # Clear existing data
    db.session.query(User).delete()
    db.session.query(Product).delete()

    # Create sample users
    users = [
        User(username='john', email='john@example.com'),
        User(username='jane', email='jane@example.com'),
        User(username='bob', email='bob@example.com'),
    ]
    db.session.add_all(users)

    # Create sample products
    products = [
        Product(name='Laptop', price=999.99, stock=50),
        Product(name='Mouse', price=29.99, stock=200),
        Product(name='Keyboard', price=79.99, stock=150),
    ]
    db.session.add_all(products)

    db.session.commit()
    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
```

### 4. Connection Pooling

```python
# Use connection pools in production

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,           # Number of connections to maintain
    max_overflow=10,       # Maximum additional connections
    pool_timeout=30,       # Timeout for getting connection
    pool_recycle=3600,     # Recycle connections after 1 hour
)
```

### 5. Backup and Restore

#### PostgreSQL
```bash
# Backup
pg_dump -U postgres -d myapp_dev -F c -f backup.dump

# Restore
pg_restore -U postgres -d myapp_dev backup.dump

# SQL format
pg_dump -U postgres myapp_dev > backup.sql
psql -U postgres myapp_dev < backup.sql
```

#### MySQL
```bash
# Backup
mysqldump -u root -p myapp_dev > backup.sql

# Restore
mysql -u root -p myapp_dev < backup.sql

# With gzip compression
mysqldump -u root -p myapp_dev | gzip > backup.sql.gz
gunzip < backup.sql.gz | mysql -u root -p myapp_dev
```

#### MongoDB
```bash
# Backup
mongodump --uri="mongodb://localhost:27017/myapp_dev" --out=backup/

# Restore
mongorestore --uri="mongodb://localhost:27017/myapp_dev" backup/myapp_dev/

# Single collection
mongodump --db=myapp_dev --collection=users --out=backup/
mongorestore --db=myapp_dev --collection=users backup/myapp_dev/users.bson
```

#### Redis
```bash
# Backup (RDB snapshot)
redis-cli SAVE  # Blocking
redis-cli BGSAVE  # Background

# Backup AOF
cp /var/lib/redis/appendonly.aof backup/

# Restore
# Stop Redis
# Copy backup file to Redis data directory
# Start Redis
```

## Troubleshooting

### PostgreSQL

**Cannot connect:**
```bash
# Check if running
pg_isready -h localhost -p 5432

# Check connections
psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Edit pg_hba.conf to allow local connections
# /etc/postgresql/15/main/pg_hba.conf
# Add: host all all 0.0.0.0/0 md5
```

**Too many connections:**
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Increase max connections in postgresql.conf
-- max_connections = 200

-- Terminate idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle' AND state_change < now() - interval '1 hour';
```

### MongoDB

**Cannot connect:**
```bash
# Check if running
mongosh --eval "db.adminCommand('ping')"

# Check mongod.conf
# bindIp: 0.0.0.0  # Allow external connections

# Restart MongoDB
sudo systemctl restart mongod
```

**Authentication failed:**
```bash
# Create admin user
mongosh
use admin
db.createUser({
  user: "admin",
  pwd: "password",
  roles: ["root"]
})

# Connect with authentication
mongosh -u admin -p password --authenticationDatabase admin
```

### Redis

**Cannot connect:**
```bash
# Check if running
redis-cli ping

# Check configuration
redis-cli CONFIG GET bind
redis-cli CONFIG GET protected-mode

# Allow remote connections
redis-cli CONFIG SET bind "0.0.0.0"
redis-cli CONFIG SET protected-mode no
```

**Memory issues:**
```bash
# Check memory usage
redis-cli INFO memory

# Set max memory
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Summary

Key setup requirements:
- **Docker Compose** for quick multi-database setup
- **Local installations** for development
- **Environment variables** for configuration
- **GUI tools** for visual management
- **Backups** for data safety
- **Connection pooling** for performance

## Next Steps

- [Docker Setup Guide](./docker-setup.md) - Detailed Docker configurations
- [Environment Variables](./environment-variables.md) - Advanced configuration
- [Backend Connectivity](../05-backend-connectivity/README.md) - Connect applications
- [Database Migrations](../07-migrations/README.md) - Schema management

---

[← Previous: Non-Relational Databases](../03-non-relational-databases/README.md) | [Next: Backend Connectivity →](../05-backend-connectivity/README.md)
