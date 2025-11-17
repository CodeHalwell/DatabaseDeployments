"""
Complete PostgreSQL Example with Python
Demonstrates CRUD operations, transactions, connection pooling, and best practices
"""

import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'tutorial_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

# Create connection pool
db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **DB_CONFIG
)

@contextmanager
def get_db_connection():
    """Context manager for database connections with automatic commit/rollback"""
    conn = db_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db_pool.putconn(conn)


class UserRepository:
    """Repository pattern for user operations"""

    @staticmethod
    def create_table():
        """Create users table if it doesn't exist"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    full_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index on email for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
            """)

            logger.info("Users table created successfully")

    @staticmethod
    def create_user(username, email, full_name=None):
        """Insert a new user"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                INSERT INTO users (username, email, full_name)
                VALUES (%s, %s, %s)
                RETURNING id, username, email, full_name, created_at
            """, (username, email, full_name))

            user = cursor.fetchone()
            logger.info(f"Created user: {user['username']}")
            return dict(user)

    @staticmethod
    def get_user_by_id(user_id):
        """Retrieve user by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, username, email, full_name, created_at, updated_at
                FROM users
                WHERE id = %s
            """, (user_id,))

            user = cursor.fetchone()
            return dict(user) if user else None

    @staticmethod
    def get_user_by_email(email):
        """Retrieve user by email (uses index)"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, username, email, full_name, created_at, updated_at
                FROM users
                WHERE email = %s
            """, (email,))

            user = cursor.fetchone()
            return dict(user) if user else None

    @staticmethod
    def get_all_users(limit=100, offset=0):
        """Retrieve all users with pagination"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, username, email, full_name, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))

            users = cursor.fetchall()
            return [dict(user) for user in users]

    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user fields dynamically"""
        if not kwargs:
            return None

        # Build dynamic UPDATE query safely
        allowed_fields = {'username', 'email', 'full_name'}
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not fields:
            return None

        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Build SET clause dynamically
            set_clause = sql.SQL(', ').join(
                sql.SQL("{} = {}").format(
                    sql.Identifier(field),
                    sql.Placeholder()
                ) for field in fields.keys()
            )

            query = sql.SQL("""
                UPDATE users
                SET {}, updated_at = CURRENT_TIMESTAMP
                WHERE id = {}
                RETURNING id, username, email, full_name, updated_at
            """).format(set_clause, sql.Placeholder())

            cursor.execute(query, (*fields.values(), user_id))
            user = cursor.fetchone()

            if user:
                logger.info(f"Updated user: {user['username']}")
                return dict(user)
            return None

    @staticmethod
    def delete_user(user_id):
        """Delete user by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            deleted = cursor.rowcount > 0

            if deleted:
                logger.info(f"Deleted user with ID: {user_id}")

            return deleted

    @staticmethod
    def search_users(search_term):
        """Search users by username or email"""
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, username, email, full_name
                FROM users
                WHERE username ILIKE %s OR email ILIKE %s
                ORDER BY username
            """, (f'%{search_term}%', f'%{search_term}%'))

            users = cursor.fetchall()
            return [dict(user) for user in users]

    @staticmethod
    def bulk_create_users(users_data):
        """Bulk insert users efficiently"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Use execute_values for efficient bulk insert
            from psycopg2.extras import execute_values

            execute_values(
                cursor,
                """
                INSERT INTO users (username, email, full_name)
                VALUES %s
                """,
                [(u['username'], u['email'], u.get('full_name')) for u in users_data]
            )

            logger.info(f"Bulk created {len(users_data)} users")


def demonstrate_crud_operations():
    """Demonstrate basic CRUD operations"""
    print("\n=== CRUD Operations Demo ===\n")

    # Create
    print("1. Creating users...")
    user1 = UserRepository.create_user(
        username="johndoe",
        email="john@example.com",
        full_name="John Doe"
    )
    print(f"   Created: {user1}")

    user2 = UserRepository.create_user(
        username="janedoe",
        email="jane@example.com",
        full_name="Jane Doe"
    )
    print(f"   Created: {user2}")

    # Read
    print("\n2. Reading user...")
    retrieved_user = UserRepository.get_user_by_id(user1['id'])
    print(f"   Retrieved: {retrieved_user}")

    # Update
    print("\n3. Updating user...")
    updated_user = UserRepository.update_user(
        user1['id'],
        full_name="John Smith"
    )
    print(f"   Updated: {updated_user}")

    # Search
    print("\n4. Searching users...")
    search_results = UserRepository.search_users("doe")
    print(f"   Found {len(search_results)} users matching 'doe'")
    for user in search_results:
        print(f"     - {user['username']}: {user['email']}")

    # List all
    print("\n5. Listing all users...")
    all_users = UserRepository.get_all_users()
    print(f"   Total users: {len(all_users)}")

    # Delete
    print("\n6. Deleting users...")
    UserRepository.delete_user(user1['id'])
    UserRepository.delete_user(user2['id'])
    print("   Users deleted")


def demonstrate_bulk_operations():
    """Demonstrate bulk insert for performance"""
    print("\n=== Bulk Operations Demo ===\n")

    print("Creating 1000 users in bulk...")
    users_data = [
        {
            'username': f'user{i}',
            'email': f'user{i}@example.com',
            'full_name': f'User Number {i}'
        }
        for i in range(1000)
    ]

    import time
    start = time.time()
    UserRepository.bulk_create_users(users_data)
    elapsed = time.time() - start

    print(f"Created 1000 users in {elapsed:.2f} seconds")

    # Cleanup
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username LIKE 'user%'")
        print(f"Cleaned up {cursor.rowcount} users")


def demonstrate_transactions():
    """Demonstrate transaction management"""
    print("\n=== Transaction Demo ===\n")

    print("Attempting transaction that will fail...")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # First insert succeeds
            cursor.execute("""
                INSERT INTO users (username, email, full_name)
                VALUES (%s, %s, %s)
            """, ('transaction_user1', 'trans1@example.com', 'Trans User 1'))
            print("  - First insert succeeded")

            # Second insert will fail (duplicate email)
            cursor.execute("""
                INSERT INTO users (username, email, full_name)
                VALUES (%s, %s, %s)
            """, ('transaction_user2', 'trans1@example.com', 'Trans User 2'))
            print("  - Second insert succeeded")

    except Exception as e:
        print(f"  - Transaction failed: {e}")
        print("  - All changes rolled back")

    # Verify rollback
    user = UserRepository.get_user_by_email('trans1@example.com')
    print(f"  - User exists after rollback: {user is not None}")


def demonstrate_query_optimization():
    """Demonstrate query optimization techniques"""
    print("\n=== Query Optimization Demo ===\n")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Explain query plan
        print("Query plan for email lookup (uses index):")
        cursor.execute("""
            EXPLAIN ANALYZE
            SELECT * FROM users WHERE email = 'john@example.com'
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}")


def main():
    """Main demonstration"""
    print("=" * 60)
    print("PostgreSQL with Python - Complete Example")
    print("=" * 60)

    try:
        # Setup
        print("\nSetting up database...")
        UserRepository.create_table()

        # Demonstrations
        demonstrate_crud_operations()
        demonstrate_bulk_operations()
        demonstrate_transactions()
        demonstrate_query_optimization()

        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise
    finally:
        # Cleanup
        if db_pool:
            db_pool.closeall()
            logger.info("Connection pool closed")


if __name__ == "__main__":
    main()
