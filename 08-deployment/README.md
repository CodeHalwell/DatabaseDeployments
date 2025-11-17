# Part 8: Database Deployment

## Overview

Deploying databases to production requires careful planning and execution. This section covers deployment strategies for major cloud providers (AWS, Google Cloud, Azure) and best practices for maintaining production database systems.

## What You'll Learn

- Cloud database services and managed offerings
- Deployment strategies and patterns
- AWS database services (RDS, DynamoDB, DocumentDB, ElastiCache)
- Google Cloud databases (Cloud SQL, Spanner, Firestore)
- Azure database services (SQL Database, Cosmos DB)
- Infrastructure as Code (Terraform, CloudFormation)
- High availability and disaster recovery
- Cost optimization strategies

## Deployment Strategies

### 1. Self-Managed on Cloud VMs

**Pros:**
- Full control over configuration
- Can use any database version
- Customizable performance tuning

**Cons:**
- Manual management (updates, backups, monitoring)
- Higher operational overhead
- Responsible for security patches

**When to use:**
- Special configuration requirements
- Cost optimization for very large databases
- Need for specific database versions

### 2. Managed Database Services

**Pros:**
- Automated backups and updates
- Built-in high availability
- Monitoring and alerting
- Reduced operational burden

**Cons:**
- Less configuration flexibility
- Potentially higher costs
- Vendor lock-in

**When to use:**
- Most production applications
- Small to medium teams
- Focus on application development

### 3. Serverless Databases

**Pros:**
- Automatic scaling
- Pay per request (cost-effective for variable loads)
- Zero server management

**Cons:**
- Cold start latency
- Limited configuration
- Different pricing model

**When to use:**
- Variable workloads
- Development/staging environments
- Microservices with unpredictable traffic

## Cloud Provider Overview

### AWS (Amazon Web Services)

#### Relational Databases
- **Amazon RDS**: Managed PostgreSQL, MySQL, MariaDB, Oracle, SQL Server
- **Amazon Aurora**: MySQL/PostgreSQL-compatible with better performance
- **Amazon Aurora Serverless**: Auto-scaling Aurora

#### NoSQL Databases
- **Amazon DynamoDB**: Fully managed key-value/document database
- **Amazon DocumentDB**: MongoDB-compatible document database
- **Amazon ElastiCache**: Managed Redis and Memcached

#### Analytics
- **Amazon Redshift**: Data warehouse
- **Amazon Timestream**: Time-series database

### Google Cloud Platform (GCP)

#### Relational Databases
- **Cloud SQL**: Managed MySQL, PostgreSQL, SQL Server
- **Cloud Spanner**: Globally distributed relational database
- **AlloyDB**: PostgreSQL-compatible database

#### NoSQL Databases
- **Firestore**: Document database (successor to Datastore)
- **Bigtable**: Wide-column database
- **Memorystore**: Managed Redis and Memcached

#### Analytics
- **BigQuery**: Data warehouse and analytics

### Microsoft Azure

#### Relational Databases
- **Azure SQL Database**: Managed SQL Server
- **Azure Database for PostgreSQL**: Managed PostgreSQL
- **Azure Database for MySQL**: Managed MySQL

#### NoSQL Databases
- **Azure Cosmos DB**: Multi-model globally distributed database
- **Azure Cache for Redis**: Managed Redis

#### Analytics
- **Azure Synapse Analytics**: Data warehouse

## Deployment Architectures

### Single-Region Architecture

```
┌─────────────────────────────────────┐
│         Load Balancer               │
└──────────┬──────────────────────────┘
           │
    ┌──────┴───────┐
    │              │
┌───▼────┐    ┌───▼────┐
│  App   │    │  App   │
│ Server │    │ Server │
└───┬────┘    └───┬────┘
    │              │
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │   Primary    │
    │   Database   │
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │  Read        │
    │  Replicas    │
    └──────────────┘
```

**Use cases:**
- Most applications
- Single geographic region
- Cost-effective
- Simpler management

### Multi-Region Architecture

```
Region 1 (Primary)              Region 2 (Standby)
┌─────────────────┐             ┌─────────────────┐
│  App Servers    │             │  App Servers    │
└────────┬────────┘             └────────┬────────┘
         │                               │
┌────────▼────────┐    Async      ┌─────▼──────────┐
│     Primary     │──Replication──→│    Replica     │
│    Database     │                │    Database    │
└─────────────────┘                └────────────────┘
```

**Use cases:**
- Global applications
- Disaster recovery
- Low-latency for different regions
- High availability requirements

### Microservices with Database per Service

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Service 1  │  │  Service 2  │  │  Service 3  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
┌──────▼──────┐  ┌──────▼──────┐  ┌─────▼───────┐
│ PostgreSQL  │  │  MongoDB    │  │   Redis     │
└─────────────┘  └─────────────┘  └─────────────┘
```

**Use cases:**
- Microservices architecture
- Independent scaling
- Technology diversity
- Service isolation

## Infrastructure as Code Examples

### AWS - Terraform

```hcl
# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier        = "myapp-db"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = "myapp"
  username = "dbadmin"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  # Backup configuration
  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  # High availability
  multi_az = true

  # Performance insights
  performance_insights_enabled = true

  # Deletion protection
  deletion_protection = true

  tags = {
    Environment = "production"
    Application = "myapp"
  }
}

# Read replica for scaling reads
resource "aws_db_instance" "replica" {
  identifier         = "myapp-db-replica"
  replicate_source_db = aws_db_instance.main.id
  instance_class     = "db.t3.medium"

  # Read replicas can be in different AZs
  availability_zone = "us-east-1b"

  tags = {
    Role = "ReadReplica"
  }
}

# DynamoDB Table
resource "aws_dynamodb_table" "sessions" {
  name           = "user-sessions"
  billing_mode   = "PAY_PER_REQUEST"  # Or "PROVISIONED"
  hash_key       = "session_id"
  range_key      = "user_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  # TTL for automatic expiration
  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Global secondary index
  global_secondary_index {
    name            = "UserIdIndex"
    hash_key        = "user_id"
    projection_type = "ALL"
  }

  tags = {
    Environment = "production"
  }
}
```

### GCP - Terraform

```hcl
# Cloud SQL PostgreSQL Instance
resource "google_sql_database_instance" "main" {
  name             = "myapp-db"
  database_version = "POSTGRES_15"
  region           = "us-central1"

  settings {
    tier              = "db-n1-standard-2"
    availability_type = "REGIONAL"  # High availability
    disk_size         = 100
    disk_type         = "PD_SSD"

    backup_configuration {
      enabled            = true
      start_time         = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
    }

    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.main.id
      require_ssl     = true
    }

    database_flags {
      name  = "max_connections"
      value = "200"
    }

    insights_config {
      query_insights_enabled = true
    }
  }

  deletion_protection = true
}

# Read replica
resource "google_sql_database_instance" "replica" {
  name                 = "myapp-db-replica"
  master_instance_name = google_sql_database_instance.main.name
  database_version     = "POSTGRES_15"
  region               = "us-east1"  # Different region

  replica_configuration {
    failover_target = false
  }

  settings {
    tier = "db-n1-standard-2"
  }
}
```

### Azure - Terraform

```hcl
# Azure SQL Database
resource "azurerm_mssql_server" "main" {
  name                         = "myapp-sqlserver"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = var.sql_password

  minimum_tls_version = "1.2"

  azuread_administrator {
    login_username = "AzureAD Admin"
    object_id      = var.azuread_admin_object_id
  }
}

resource "azurerm_mssql_database" "main" {
  name      = "myapp-db"
  server_id = azurerm_mssql_server.main.id
  sku_name  = "S2"  # Standard tier

  # Long-term retention
  long_term_retention_policy {
    weekly_retention  = "P1W"
    monthly_retention = "P1M"
    yearly_retention  = "P1Y"
    week_of_year      = 1
  }

  # Threat detection
  threat_detection_policy {
    state                      = "Enabled"
    email_account_admins       = "Enabled"
    retention_days             = 30
  }
}

# Cosmos DB (globally distributed)
resource "azurerm_cosmosdb_account" "main" {
  name                = "myapp-cosmos"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level = "Session"
  }

  # Multi-region
  geo_location {
    location          = "eastus"
    failover_priority = 0
  }

  geo_location {
    location          = "westus"
    failover_priority = 1
  }

  # Automatic failover
  enable_automatic_failover = true
}
```

## Connection String Management

### Environment Variables

```python
# .env file (never commit to git!)
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://localhost:6379/0
MONGODB_URI=mongodb://user:password@host:27017/dbname

# Python application
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
```

### AWS Secrets Manager

```python
import boto3
from botocore.exceptions import ClientError
import json

def get_secret(secret_name, region_name="us-east-1"):
    """Retrieve secret from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        raise e

# Usage
db_credentials = get_secret('production/database/credentials')
DATABASE_URL = f"postgresql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}:5432/{db_credentials['database']}"
```

### Google Cloud Secret Manager

```python
from google.cloud import secretmanager

def get_secret(project_id, secret_id, version_id="latest"):
    """Retrieve secret from Google Cloud Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

# Usage
DATABASE_URL = get_secret('my-project', 'database-url')
```

### Azure Key Vault

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret(vault_url, secret_name):
    """Retrieve secret from Azure Key Vault"""
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    secret = client.get_secret(secret_name)
    return secret.value

# Usage
vault_url = "https://myapp-keyvault.vault.azure.net"
DATABASE_URL = get_secret(vault_url, "database-url")
```

## Deployment Checklist

### Pre-Deployment

- [ ] Choose appropriate database type and size
- [ ] Plan for high availability (multi-AZ, replicas)
- [ ] Configure backups and retention
- [ ] Set up monitoring and alerting
- [ ] Implement security groups/firewall rules
- [ ] Enable encryption at rest and in transit
- [ ] Configure automated backups
- [ ] Test disaster recovery procedures
- [ ] Document connection procedures
- [ ] Set up secrets management

### Post-Deployment

- [ ] Verify connectivity from application
- [ ] Test failover procedures
- [ ] Configure monitoring dashboards
- [ ] Set up alerting thresholds
- [ ] Perform initial backup
- [ ] Document operational procedures
- [ ] Train team on management tools
- [ ] Schedule regular maintenance windows
- [ ] Review and optimize costs
- [ ] Conduct security audit

## Monitoring and Observability

### Key Metrics to Monitor

```python
# Example: CloudWatch metrics for RDS
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

def get_database_metrics(db_instance_id):
    """Retrieve key database metrics"""
    metrics = {
        'CPUUtilization': get_metric(db_instance_id, 'CPUUtilization'),
        'DatabaseConnections': get_metric(db_instance_id, 'DatabaseConnections'),
        'FreeableMemory': get_metric(db_instance_id, 'FreeableMemory'),
        'ReadLatency': get_metric(db_instance_id, 'ReadLatency'),
        'WriteLatency': get_metric(db_instance_id, 'WriteLatency'),
        'FreeStorageSpace': get_metric(db_instance_id, 'FreeStorageSpace'),
    }
    return metrics

def get_metric(db_instance_id, metric_name, period=300):
    """Get CloudWatch metric statistics"""
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/RDS',
        MetricName=metric_name,
        Dimensions=[
            {'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}
        ],
        StartTime=datetime.now() - timedelta(hours=1),
        EndTime=datetime.now(),
        Period=period,
        Statistics=['Average', 'Maximum']
    )
    return response['Datapoints']
```

### Alerting Configuration

```yaml
# Example: CloudWatch Alarm (CloudFormation)
DatabaseHighCPUAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmDescription: Alert when database CPU exceeds 80%
    MetricName: CPUUtilization
    Namespace: AWS/RDS
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 80
    ComparisonOperator: GreaterThanThreshold
    Dimensions:
      - Name: DBInstanceIdentifier
        Value: !Ref DBInstance
    AlarmActions:
      - !Ref SNSTopic

DatabaseConnectionsAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmDescription: Alert when connections exceed 90% of max
    MetricName: DatabaseConnections
    Namespace: AWS/RDS
    Statistic: Average
    Period: 300
    EvaluationPeriods: 2
    Threshold: 180  # 90% of 200 max connections
    ComparisonOperator: GreaterThanThreshold
    Dimensions:
      - Name: DBInstanceIdentifier
        Value: !Ref DBInstance
    AlarmActions:
      - !Ref SNSTopic
```

## Cost Optimization

### Strategies

1. **Right-sizing**: Match instance size to workload
2. **Reserved Instances**: Save up to 50% with 1-3 year commitments
3. **Spot Instances**: Use for non-production (up to 90% savings)
4. **Automatic Scaling**: Scale down during low-traffic periods
5. **Read Replicas**: Offload read traffic from primary
6. **Data Lifecycle**: Archive old data to cheaper storage
7. **Compression**: Enable database compression
8. **Monitoring**: Identify and eliminate waste

### Cost Analysis Example

```python
# AWS Cost Explorer API
import boto3
from datetime import datetime, timedelta

ce = boto3.client('ce', region_name='us-east-1')

def get_database_costs(days=30):
    """Get database costs for the last N days"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.isoformat(),
            'End': end_date.isoformat()
        },
        Granularity='DAILY',
        Filter={
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': ['Amazon RDS', 'Amazon DynamoDB']
            }
        },
        Metrics=['UnblendedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'},
            {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
        ]
    )

    return response['ResultsByTime']
```

## Section Contents

### [Deployment Strategies Overview](./strategies.md)
Comprehensive guide to different deployment approaches and when to use them.

### [AWS Deployment](./aws/README.md)
- [RDS (Relational Database Service)](./aws/rds.md)
- [DynamoDB](./aws/dynamodb.md)
- [DocumentDB (MongoDB Compatible)](./aws/documentdb.md)
- [ElastiCache (Redis/Memcached)](./aws/elasticache.md)

### [Google Cloud Deployment](./gcp/README.md)
- [Cloud SQL](./gcp/cloud-sql.md)
- [Cloud Spanner](./gcp/cloud-spanner.md)
- [Firestore](./gcp/firestore.md)
- [Memorystore (Redis)](./gcp/memorystore.md)

### [Azure Deployment](./azure/README.md)
- [Azure SQL Database](./azure/sql-database.md)
- [Cosmos DB](./azure/cosmos-db.md)
- [Azure Database for PostgreSQL/MySQL](./azure/postgresql-mysql.md)
- [Azure Cache for Redis](./azure/redis-cache.md)

### [Multi-Cloud Strategies](./multi-cloud.md)
Approaches for deploying across multiple cloud providers.

## Summary

Key takeaways for database deployment:

1. **Choose Managed Services**: Unless you have specific requirements
2. **Plan for High Availability**: Multi-AZ, read replicas, automated backups
3. **Security First**: Encryption, secrets management, network isolation
4. **Monitor Everything**: CPU, memory, connections, query performance
5. **Automate**: Use Infrastructure as Code (Terraform, CloudFormation)
6. **Cost Optimize**: Right-size, use reserved instances, monitor usage
7. **Test Failover**: Regularly test disaster recovery procedures

## Next Steps

- [Performance Optimization](../09-performance/README.md) - Optimize deployed databases
- [Security Best Practices](../10-security/README.md) - Secure production databases
- [Scaling Strategies](../11-scaling/README.md) - Scale deployed databases

---

[← Previous: Migrations](../07-migrations/README.md) | [Next: Performance Optimization →](../09-performance/README.md)
