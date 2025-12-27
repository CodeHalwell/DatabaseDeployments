# Part 10: Database Security Best Practices

## Overview

Database security is critical for protecting sensitive data, maintaining compliance, and preventing breaches. This section covers essential security practices from development through production deployment.

## What You'll Learn

- SQL injection prevention
- Authentication and authorization
- Encryption (at rest and in transit)
- Network security and firewalls
- Backup and disaster recovery
- Compliance requirements (GDPR, HIPAA, etc.)
- Security auditing and monitoring
- Common vulnerabilities and mitigations

## SQL Injection Prevention

### What is SQL Injection?

SQL injection occurs when untrusted user input is inserted directly into SQL queries, allowing attackers to execute arbitrary SQL commands.

### Vulnerable Code Examples

```python
# ❌ DANGEROUS: String formatting
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()

# Attack:
get_user("admin' OR '1'='1")
# Results in: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# Returns all users!

# ❌ DANGEROUS: String concatenation
def login(username, password):
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    return cursor.fetchone()

# Attack:
login("admin", "' OR '1'='1")
# Results in: SELECT * FROM users WHERE username = 'admin' AND password = '' OR '1'='1'
# Bypasses authentication!
```

### Safe Code Examples

```python
# ✅ SAFE: Parameterized queries
def get_user(username):
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    return cursor.fetchone()

# The database driver escapes the parameter safely
# Attack attempt: username = "admin' OR '1'='1"
# Results in: SELECT * FROM users WHERE username = 'admin'' OR ''1''=''1'
# Treats entire input as a string - attack fails!

# ✅ SAFE: SQLAlchemy (ORM)
from sqlalchemy import select

def get_user(username):
    stmt = select(User).where(User.username == username)
    result = session.execute(stmt)
    return result.scalars().first()

# ORM automatically uses parameterized queries
```

### Prevention Checklist

```python
# ✅ DO: Use parameterized queries
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ✅ DO: Use ORMs (SQLAlchemy, Django ORM)
User.query.filter_by(username=username).first()

# ✅ DO: Validate and sanitize input
def validate_username(username):
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise ValueError("Invalid username format")
    return username

# ✅ DO: Use prepared statements
stmt = cursor.prepare("SELECT * FROM users WHERE id = ?")
stmt.execute((user_id,))

# ❌ DON'T: Use string formatting
query = f"SELECT * FROM users WHERE id = {user_id}"  # NEVER!

# ❌ DON'T: Trust user input
query = "SELECT * FROM users WHERE username = '" + username + "'"  # NEVER!

# ❌ DON'T: Build dynamic column/table names from user input
table_name = request.args.get('table')  # User-controlled
query = f"SELECT * FROM {table_name}"  # DANGEROUS!
```

### MongoDB Injection Prevention

```python
# ❌ DANGEROUS: JavaScript in queries
def find_user(username):
    # Don't use $where with user input
    return users.find({
        '$where': f"this.username == '{username}'"
    })

# ✅ SAFE: Normal queries
def find_user(username):
    return users.find_one({'username': username})

# ✅ SAFE: Validate input
def find_users_by_age(min_age):
    # Validate input type
    if not isinstance(min_age, int):
        raise ValueError("Age must be an integer")

    return list(users.find({'age': {'$gte': min_age}}))
```

## Authentication and Authorization

### Database Users and Roles

#### PostgreSQL

```sql
-- Create roles
CREATE ROLE readonly;
CREATE ROLE readwrite;
CREATE ROLE admin;

-- Grant permissions
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO readwrite;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;

-- Create users with roles
CREATE USER app_reader WITH PASSWORD 'strong_password';
GRANT readonly TO app_reader;

CREATE USER app_writer WITH PASSWORD 'strong_password';
GRANT readwrite TO app_writer;

-- Revoke public permissions
REVOKE ALL ON DATABASE myapp FROM PUBLIC;

-- Row-level security
CREATE POLICY user_data_policy ON users
    FOR SELECT
    USING (id = current_user_id());

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
```

#### MySQL

```sql
-- Create users
CREATE USER 'app_readonly'@'%' IDENTIFIED BY 'strong_password';
CREATE USER 'app_readwrite'@'%' IDENTIFIED BY 'strong_password';

-- Grant permissions
GRANT SELECT ON myapp.* TO 'app_readonly'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON myapp.* TO 'app_readwrite'@'%';

-- Flush privileges
FLUSH PRIVILEGES;

-- Restrict by IP
CREATE USER 'app_user'@'10.0.1.%' IDENTIFIED BY 'strong_password';
GRANT ALL ON myapp.* TO 'app_user'@'10.0.1.%';
```

#### MongoDB

```javascript
// Create admin user
use admin
db.createUser({
  user: "admin",
  pwd: "strong_password",
  roles: ["root"]
})

// Create application users
use myapp
db.createUser({
  user: "app_readonly",
  pwd: "strong_password",
  roles: [
    { role: "read", db: "myapp" }
  ]
})

db.createUser({
  user: "app_readwrite",
  pwd: "strong_password",
  roles: [
    { role: "readWrite", db: "myapp" }
  ]
})

// Enable authentication (mongod.conf)
// security:
//   authorization: enabled
```

### Application-Level Authorization

```python
from functools import wraps
from flask import request, jsonify

def require_permission(permission):
    """Decorator to check permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({'error': 'Unauthorized'}), 401

            if permission not in user.permissions:
                return jsonify({'error': 'Forbidden'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/admin/users')
@require_permission('admin.users.read')
def list_users():
    """Only users with admin.users.read permission can access"""
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@require_permission('admin.users.delete')
def delete_user(user_id):
    """Only users with admin.users.delete permission can access"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204
```

## Encryption

### Encryption at Rest

#### PostgreSQL: pgcrypto

```sql
-- Enable pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive data
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    ssn BYTEA,  -- Encrypted field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert encrypted data
INSERT INTO users (email, ssn)
VALUES (
    'john@example.com',
    pgp_sym_encrypt('123-45-6789', 'encryption_key')
);

-- Retrieve and decrypt
SELECT
    email,
    pgp_sym_decrypt(ssn, 'encryption_key') AS ssn
FROM users
WHERE email = 'john@example.com';
```

#### Application-Level Encryption (Python)

```python
from cryptography.fernet import Fernet
import os

class EncryptedField:
    """Encrypt/decrypt sensitive fields"""

    def __init__(self):
        # Load encryption key from environment
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY not set")
        self.cipher = Fernet(key.encode())

    def encrypt(self, value):
        """Encrypt a value"""
        if value is None:
            return None
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt(self, encrypted_value):
        """Decrypt a value"""
        if encrypted_value is None:
            return None
        return self.cipher.decrypt(encrypted_value.encode()).decode()

# Usage
encryptor = EncryptedField()

# Encrypt before storing
ssn_encrypted = encryptor.encrypt('123-45-6789')
cursor.execute(
    "INSERT INTO users (email, ssn) VALUES (%s, %s)",
    ('john@example.com', ssn_encrypted)
)

# Decrypt when retrieving
cursor.execute("SELECT ssn FROM users WHERE email = %s", ('john@example.com',))
ssn_encrypted = cursor.fetchone()[0]
ssn = encryptor.decrypt(ssn_encrypted)
```

### Encryption in Transit (TLS/SSL)

#### PostgreSQL

```python
# Require SSL connection
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='myapp',
    user='postgres',
    password='password',
    sslmode='require'  # or 'verify-full' for certificate verification
)

# With certificate verification
conn = psycopg2.connect(
    host='prod-db.example.com',
    database='myapp',
    user='app_user',
    password='password',
    sslmode='verify-full',
    sslrootcert='/path/to/root.crt',
    sslcert='/path/to/client.crt',
    sslkey='/path/to/client.key'
)
```

#### MySQL

```python
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    database='myapp',
    user='app_user',
    password='password',
    ssl_ca='/path/to/ca-cert.pem',
    ssl_disabled=False
)
```

#### MongoDB

```python
from pymongo import MongoClient

# Connect with TLS
client = MongoClient(
    'mongodb://user:password@hostname:27017/',
    tls=True,
    tlsCAFile='/path/to/ca-cert.pem',
    tlsCertificateKeyFile='/path/to/client-cert.pem'
)

# Or using connection string
client = MongoClient(
    'mongodb://user:password@hostname:27017/?tls=true&tlsCAFile=/path/to/ca.pem'
)
```

## Network Security

### Firewall Configuration

```bash
# UFW (Ubuntu)
# Allow only specific IPs to access PostgreSQL
sudo ufw allow from 10.0.1.0/24 to any port 5432
sudo ufw deny 5432

# Allow application server subnet
sudo ufw allow from 172.31.0.0/16 to any port 5432

# Enable firewall
sudo ufw enable

# iptables
# Allow specific IP
sudo iptables -A INPUT -p tcp -s 10.0.1.50 --dport 5432 -j ACCEPT

# Drop all other PostgreSQL connections
sudo iptables -A INPUT -p tcp --dport 5432 -j DROP
```

### Database Configuration

#### PostgreSQL: pg_hba.conf

```conf
# /etc/postgresql/15/main/pg_hba.conf

# Type  Database    User        Address         Auth Method
# Local connections
local   all         postgres                    peer
local   all         all                         md5

# IPv4 connections
# Reject all external connections
host    all         all         0.0.0.0/0       reject

# Allow specific subnet only
host    all         app_user    10.0.1.0/24     md5
host    all         app_user    172.31.0.0/16   md5

# Require SSL for production
hostssl all         all         10.0.0.0/8      md5
```

#### MySQL: bind-address

```ini
# /etc/mysql/mysql.conf.d/mysqld.cnf

[mysqld]
# Only listen on private IP
bind-address = 10.0.1.10

# Don't listen on public interface
# bind-address = 0.0.0.0  # DANGEROUS!
```

#### MongoDB: bindIp

```yaml
# /etc/mongod.conf

net:
  port: 27017
  bindIp: 127.0.0.1,10.0.1.10  # localhost + private IP only
```

### VPC and Private Networks

```python
# AWS RDS: Launch in private subnet
# Security group: Allow only from application servers

# Connection from application server (in same VPC)
conn = psycopg2.connect(
    host='mydb.abc123.us-east-1.rds.amazonaws.com',  # Private DNS
    database='myapp',
    user='app_user',
    password=os.getenv('DB_PASSWORD')
)

# Database is NOT accessible from internet
# Only from within VPC
```

## Secrets Management

### Environment Variables

```python
# .env file (NEVER commit to git!)
DATABASE_URL=postgresql://user:password@host:5432/db
ENCRYPTION_KEY=your-encryption-key-here
API_KEY=your-api-key-here

# .gitignore
.env
.env.local
.env.*.local
```

### AWS Secrets Manager

```python
import boto3
import json

def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name='us-east-1')

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        raise Exception(f"Failed to retrieve secret: {e}")

# Usage
db_credentials = get_secret('production/database/credentials')
DATABASE_URL = f"postgresql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}:5432/{db_credentials['database']}"
```

### HashiCorp Vault

```python
import hvac

# Connect to Vault
client = hvac.Client(url='https://vault.example.com:8200')
client.token = os.getenv('VAULT_TOKEN')

# Read secret
secret = client.secrets.kv.v2.read_secret_version(
    path='database/production'
)

db_credentials = secret['data']['data']
DATABASE_URL = db_credentials['connection_string']
```

## Backup and Disaster Recovery

### Automated Backups

#### PostgreSQL

```bash
#!/bin/bash
# backup_postgres.sh

DB_NAME="myapp"
DB_USER="postgres"
BACKUP_DIR="/var/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="$BACKUP_DIR/${DB_NAME}_${DATE}.dump"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
pg_dump -U $DB_USER -F c -b -v -f "$FILENAME" $DB_NAME

# Compress
gzip "$FILENAME"

# Upload to S3
aws s3 cp "${FILENAME}.gz" s3://my-backups/postgres/

# Delete local backups older than 7 days
find $BACKUP_DIR -name "*.dump.gz" -mtime +7 -delete

echo "Backup completed: ${FILENAME}.gz"
```

#### MongoDB

```bash
#!/bin/bash
# backup_mongodb.sh

DB_NAME="myapp"
BACKUP_DIR="/var/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
mongodump --uri="mongodb://localhost:27017/$DB_NAME" --out="$BACKUP_DIR/$DATE"

# Compress
tar -czf "$BACKUP_DIR/${DB_NAME}_${DATE}.tar.gz" -C "$BACKUP_DIR" "$DATE"

# Upload to S3
aws s3 cp "$BACKUP_DIR/${DB_NAME}_${DATE}.tar.gz" s3://my-backups/mongodb/

# Cleanup
rm -rf "$BACKUP_DIR/$DATE"
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Point-in-Time Recovery (PITR)

#### PostgreSQL: WAL Archiving

```ini
# postgresql.conf

# Enable WAL archiving
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/wal_archive/%f && cp %p /var/lib/postgresql/wal_archive/%f'

# Continuous archiving to S3
archive_command = 'aws s3 cp %p s3://my-wal-archive/%f'

# Restore to specific point in time
# 1. Stop PostgreSQL
# 2. Restore base backup
# 3. Create recovery.conf:
#    restore_command = 'aws s3 cp s3://my-wal-archive/%f %p'
#    recovery_target_time = '2024-01-15 14:30:00'
# 4. Start PostgreSQL
```

### Testing Backups

```python
#!/usr/bin/env python3
"""Test database backup restoration"""

import subprocess
import psycopg2
import sys

def test_backup_restore(backup_file):
    """Test restoring a backup"""
    test_db = 'test_restore_db'

    try:
        # Drop test database if exists
        subprocess.run(['dropdb', '--if-exists', test_db])

        # Create test database
        subprocess.run(['createdb', test_db], check=True)

        # Restore backup
        result = subprocess.run(
            ['pg_restore', '-d', test_db, backup_file],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Restore failed: {result.stderr}")
            return False

        # Verify data
        conn = psycopg2.connect(database=test_db)
        cursor = conn.cursor()

        # Check table count
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]

        if table_count == 0:
            print("Restore failed: No tables found")
            return False

        print(f"Restore successful: {table_count} tables restored")

        conn.close()
        return True

    finally:
        # Cleanup
        subprocess.run(['dropdb', '--if-exists', test_db])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: test_backup.py <backup_file>")
        sys.exit(1)

    success = test_backup_restore(sys.argv[1])
    sys.exit(0 if success else 1)
```

## Auditing and Monitoring

### Audit Logging

```sql
-- PostgreSQL: pgAudit extension
CREATE EXTENSION pgaudit;

-- Log all DDL statements
ALTER SYSTEM SET pgaudit.log = 'ddl';

-- Log all reads and writes to sensitive tables
ALTER TABLE users SET (pgaudit.log = 'read, write');

-- View audit logs
SELECT * FROM pg_stat_activity;
```

### Application-Level Audit Trail

```python
from datetime import datetime
import json

class AuditLog:
    """Audit trail for sensitive operations"""

    @staticmethod
    def log_action(user_id, action, table, record_id, changes=None):
        """Log a database action"""
        cursor.execute("""
            INSERT INTO audit_log (
                user_id, action, table_name, record_id,
                changes, ip_address, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            action,  # 'INSERT', 'UPDATE', 'DELETE'
            table,
            record_id,
            json.dumps(changes) if changes else None,
            request.remote_addr,
            datetime.utcnow()
        ))
        conn.commit()

# Usage
def update_user(user_id, updates):
    """Update user with audit trail"""
    # Get current state
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    old_state = cursor.fetchone()

    # Perform update
    cursor.execute("""
        UPDATE users
        SET username = %s, email = %s
        WHERE id = %s
    """, (updates['username'], updates['email'], user_id))

    # Log change
    AuditLog.log_action(
        user_id=current_user_id(),
        action='UPDATE',
        table='users',
        record_id=user_id,
        changes={
            'old': dict(old_state),
            'new': updates
        }
    )

    conn.commit()
```

### Security Monitoring

```python
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityMonitor:
    """Monitor for suspicious activities"""

    @staticmethod
    def detect_brute_force(username):
        """Detect brute force login attempts"""
        # Check failed login attempts in last 10 minutes
        cursor.execute("""
            SELECT COUNT(*)
            FROM login_attempts
            WHERE username = %s
                AND success = FALSE
                AND timestamp > %s
        """, (username, datetime.utcnow() - timedelta(minutes=10)))

        failed_attempts = cursor.fetchone()[0]

        if failed_attempts >= 5:
            logger.warning(f"Brute force detected for user: {username}")
            # Lock account or add delay
            return True

        return False

    @staticmethod
    def detect_sql_injection(query):
        """Detect potential SQL injection attempts"""
        suspicious_patterns = [
            "' OR '1'='1",
            "'; DROP TABLE",
            "UNION SELECT",
            "' OR 1=1--"
        ]

        for pattern in suspicious_patterns:
            if pattern.lower() in query.lower():
                logger.error(f"SQL injection attempt detected: {query}")
                # Alert security team
                return True

        return False
```

## Compliance Requirements

### GDPR (General Data Protection Regulation)

```python
class GDPRCompliance:
    """GDPR compliance features"""

    @staticmethod
    def export_user_data(user_id):
        """Export all user data (Right to data portability)"""
        data = {}

        # User profile
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        data['profile'] = cursor.fetchone()

        # Orders
        cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
        data['orders'] = cursor.fetchall()

        # Activity logs
        cursor.execute("SELECT * FROM user_activities WHERE user_id = %s", (user_id,))
        data['activities'] = cursor.fetchall()

        return json.dumps(data, default=str)

    @staticmethod
    def delete_user_data(user_id):
        """Delete all user data (Right to erasure)"""
        # Anonymize instead of delete for audit compliance
        cursor.execute("""
            UPDATE users
            SET
                email = CONCAT('deleted_', id, '@deleted.com'),
                username = CONCAT('deleted_', id),
                first_name = 'DELETED',
                last_name = 'DELETED',
                deleted_at = NOW()
            WHERE id = %s
        """, (user_id,))

        # Actually delete non-essential data
        cursor.execute("DELETE FROM user_activities WHERE user_id = %s", (user_id,))

        conn.commit()
```

## Security Checklist

### Development
- [ ] Use parameterized queries for all database operations
- [ ] Validate and sanitize all user input
- [ ] Use ORMs to prevent SQL injection
- [ ] Never log sensitive data (passwords, tokens, credit cards)
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting for authentication endpoints

### Database Configuration
- [ ] Change default passwords
- [ ] Create application-specific database users
- [ ] Grant minimum required permissions (principle of least privilege)
- [ ] Enable authentication
- [ ] Disable unnecessary features and extensions
- [ ] Keep database software updated

### Network Security
- [ ] Use private networks (VPC) for databases
- [ ] Configure firewall rules (allow only application servers)
- [ ] Use TLS/SSL for all connections
- [ ] Implement network segmentation
- [ ] Use bastion hosts for administrative access

### Encryption
- [ ] Enable encryption at rest
- [ ] Use TLS/SSL for connections (encryption in transit)
- [ ] Encrypt sensitive fields in application
- [ ] Securely store encryption keys (separate from data)
- [ ] Implement key rotation

### Backup and Recovery
- [ ] Automate regular backups
- [ ] Store backups in separate location
- [ ] Encrypt backup files
- [ ] Test restore procedures regularly
- [ ] Implement point-in-time recovery
- [ ] Document recovery procedures

### Monitoring and Auditing
- [ ] Enable query logging
- [ ] Monitor failed authentication attempts
- [ ] Set up alerts for suspicious activities
- [ ] Implement audit trails for sensitive operations
- [ ] Regular security audits
- [ ] Review access logs

### Compliance
- [ ] Understand regulatory requirements (GDPR, HIPAA, etc.)
- [ ] Implement data retention policies
- [ ] Provide data export capabilities
- [ ] Implement data deletion procedures
- [ ] Maintain audit trails
- [ ] Document security procedures

## Summary

Database security requires a multi-layered approach:

1. **Prevent SQL Injection**: Use parameterized queries always
2. **Strong Authentication**: Implement robust user management
3. **Encrypt Data**: At rest and in transit
4. **Network Security**: Firewalls, VPCs, private networks
5. **Secrets Management**: Never hardcode credentials
6. **Regular Backups**: Automated, tested, encrypted
7. **Monitoring**: Detect and respond to threats
8. **Compliance**: Meet regulatory requirements

Security is not a one-time task but an ongoing process!

## Next Steps

- [Scaling Strategies](../11-scaling/README.md) - Scale securely
- [Deployment Guide](../08-deployment/README.md) - Secure deployment
- [Performance Optimization](../09-performance/README.md) - Secure and fast

---

[← Previous: Performance](../09-performance/README.md) | [Next: Scaling →](../11-scaling/README.md)
