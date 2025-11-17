"""
Complete MongoDB Example with Python
Demonstrates CRUD operations, aggregations, indexing, and best practices
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = 'tutorial_db'

# Initialize client
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DATABASE_NAME]


class ProductRepository:
    """Repository for product operations"""

    collection = db['products']

    @classmethod
    def setup_indexes(cls):
        """Create indexes for better query performance"""
        # Single field index
        cls.collection.create_index([('sku', ASCENDING)], unique=True)

        # Compound index
        cls.collection.create_index([
            ('category', ASCENDING),
            ('price', DESCENDING)
        ])

        # Text index for full-text search
        cls.collection.create_index([
            ('name', 'text'),
            ('description', 'text')
        ])

        logger.info("Indexes created successfully")

    @classmethod
    def create_product(cls, product_data):
        """Insert a new product"""
        product = {
            'sku': product_data['sku'],
            'name': product_data['name'],
            'description': product_data.get('description', ''),
            'category': product_data['category'],
            'price': product_data['price'],
            'stock': product_data.get('stock', 0),
            'tags': product_data.get('tags', []),
            'specifications': product_data.get('specifications', {}),
            'ratings': {
                'average': 0,
                'count': 0
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = cls.collection.insert_one(product)
        product['_id'] = result.inserted_id

        logger.info(f"Created product: {product['name']}")
        return product

    @classmethod
    def get_product_by_sku(cls, sku):
        """Retrieve product by SKU"""
        return cls.collection.find_one({'sku': sku})

    @classmethod
    def get_product_by_id(cls, product_id):
        """Retrieve product by ID"""
        from bson import ObjectId
        return cls.collection.find_one({'_id': ObjectId(product_id)})

    @classmethod
    def update_product(cls, sku, update_data):
        """Update product fields"""
        update_data['updated_at'] = datetime.utcnow()

        result = cls.collection.update_one(
            {'sku': sku},
            {'$set': update_data}
        )

        if result.modified_count > 0:
            logger.info(f"Updated product: {sku}")
            return cls.get_product_by_sku(sku)
        return None

    @classmethod
    def delete_product(cls, sku):
        """Delete product by SKU"""
        result = cls.collection.delete_one({'sku': sku})

        if result.deleted_count > 0:
            logger.info(f"Deleted product: {sku}")
            return True
        return False

    @classmethod
    def search_products(cls, search_term):
        """Full-text search on products"""
        return list(cls.collection.find(
            {'$text': {'$search': search_term}},
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})]))

    @classmethod
    def get_products_by_category(cls, category, limit=10):
        """Get products by category"""
        return list(cls.collection.find(
            {'category': category}
        ).sort('price', DESCENDING).limit(limit))

    @classmethod
    def get_products_in_price_range(cls, min_price, max_price):
        """Get products within price range"""
        return list(cls.collection.find({
            'price': {'$gte': min_price, '$lte': max_price}
        }).sort('price', ASCENDING))

    @classmethod
    def add_rating(cls, sku, rating, review):
        """Add a product rating"""
        product = cls.get_product_by_sku(sku)
        if not product:
            return None

        # Initialize reviews array if it doesn't exist
        if 'reviews' not in product:
            cls.collection.update_one(
                {'sku': sku},
                {'$set': {'reviews': []}}
            )

        # Add review
        cls.collection.update_one(
            {'sku': sku},
            {
                '$push': {
                    'reviews': {
                        'rating': rating,
                        'comment': review,
                        'date': datetime.utcnow()
                    }
                }
            }
        )

        # Recalculate average rating
        pipeline = [
            {'$match': {'sku': sku}},
            {'$unwind': '$reviews'},
            {
                '$group': {
                    '_id': '$_id',
                    'average_rating': {'$avg': '$reviews.rating'},
                    'rating_count': {'$sum': 1}
                }
            }
        ]

        result = list(cls.collection.aggregate(pipeline))
        if result:
            cls.collection.update_one(
                {'sku': sku},
                {
                    '$set': {
                        'ratings.average': round(result[0]['average_rating'], 2),
                        'ratings.count': result[0]['rating_count']
                    }
                }
            )

        logger.info(f"Added rating for product: {sku}")
        return cls.get_product_by_sku(sku)

    @classmethod
    def update_stock(cls, sku, quantity_change):
        """Update product stock (increment/decrement)"""
        result = cls.collection.update_one(
            {'sku': sku},
            {
                '$inc': {'stock': quantity_change},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            return cls.get_product_by_sku(sku)
        return None

    @classmethod
    def bulk_create_products(cls, products_data):
        """Bulk insert products"""
        products = [
            {
                **product_data,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            for product_data in products_data
        ]

        result = cls.collection.insert_many(products)
        logger.info(f"Bulk created {len(result.inserted_ids)} products")
        return result.inserted_ids

    @classmethod
    def get_category_statistics(cls):
        """Aggregate statistics by category"""
        pipeline = [
            {
                '$group': {
                    '_id': '$category',
                    'product_count': {'$sum': 1},
                    'avg_price': {'$avg': '$price'},
                    'min_price': {'$min': '$price'},
                    'max_price': {'$max': '$price'},
                    'total_stock': {'$sum': '$stock'}
                }
            },
            {
                '$sort': {'product_count': -1}
            }
        ]

        return list(cls.collection.aggregate(pipeline))

    @classmethod
    def get_low_stock_products(cls, threshold=10):
        """Find products with low stock"""
        return list(cls.collection.find(
            {'stock': {'$lte': threshold}}
        ).sort('stock', ASCENDING))

    @classmethod
    def get_top_rated_products(cls, limit=10):
        """Get top-rated products"""
        return list(cls.collection.find(
            {'ratings.count': {'$gte': 5}}  # At least 5 ratings
        ).sort('ratings.average', DESCENDING).limit(limit))


def demonstrate_crud_operations():
    """Demonstrate basic CRUD operations"""
    print("\n=== MongoDB CRUD Operations Demo ===\n")

    # Create
    print("1. Creating products...")
    product1 = ProductRepository.create_product({
        'sku': 'LAPTOP-001',
        'name': 'Premium Laptop',
        'description': 'High-performance laptop for professionals',
        'category': 'Electronics',
        'price': 1299.99,
        'stock': 50,
        'tags': ['laptop', 'computer', 'premium'],
        'specifications': {
            'cpu': 'Intel i7',
            'ram': '16GB',
            'storage': '512GB SSD'
        }
    })
    print(f"   Created: {product1['name']} (SKU: {product1['sku']})")

    product2 = ProductRepository.create_product({
        'sku': 'MOUSE-001',
        'name': 'Wireless Mouse',
        'description': 'Ergonomic wireless mouse',
        'category': 'Electronics',
        'price': 29.99,
        'stock': 200,
        'tags': ['mouse', 'wireless', 'ergonomic']
    })
    print(f"   Created: {product2['name']} (SKU: {product2['sku']})")

    # Read
    print("\n2. Reading product...")
    retrieved = ProductRepository.get_product_by_sku('LAPTOP-001')
    print(f"   Retrieved: {retrieved['name']} - ${retrieved['price']}")

    # Update
    print("\n3. Updating product...")
    updated = ProductRepository.update_product('LAPTOP-001', {
        'price': 1199.99,
        'stock': 45
    })
    print(f"   Updated price: ${updated['price']}")

    # Add ratings
    print("\n4. Adding product ratings...")
    ProductRepository.add_rating('LAPTOP-001', 5, 'Excellent laptop!')
    ProductRepository.add_rating('LAPTOP-001', 4, 'Great performance')
    ProductRepository.add_rating('LAPTOP-001', 5, 'Highly recommended')
    rated_product = ProductRepository.get_product_by_sku('LAPTOP-001')
    print(f"   Average rating: {rated_product['ratings']['average']} "
          f"({rated_product['ratings']['count']} reviews)")


def demonstrate_queries():
    """Demonstrate various query operations"""
    print("\n=== Query Operations Demo ===\n")

    # Search
    print("1. Full-text search for 'laptop'...")
    results = ProductRepository.search_products('laptop')
    print(f"   Found {len(results)} products")
    for product in results:
        print(f"     - {product['name']}: ${product['price']}")

    # Category query
    print("\n2. Products in 'Electronics' category...")
    electronics = ProductRepository.get_products_by_category('Electronics')
    print(f"   Found {len(electronics)} products")

    # Price range query
    print("\n3. Products between $20 and $100...")
    in_range = ProductRepository.get_products_in_price_range(20, 100)
    print(f"   Found {len(in_range)} products")


def demonstrate_aggregations():
    """Demonstrate aggregation pipeline"""
    print("\n=== Aggregation Pipeline Demo ===\n")

    print("Category statistics:")
    stats = ProductRepository.get_category_statistics()
    for stat in stats:
        print(f"\n   Category: {stat['_id']}")
        print(f"   - Products: {stat['product_count']}")
        print(f"   - Avg Price: ${stat['avg_price']:.2f}")
        print(f"   - Price Range: ${stat['min_price']:.2f} - ${stat['max_price']:.2f}")
        print(f"   - Total Stock: {stat['total_stock']}")


def demonstrate_array_operations():
    """Demonstrate working with arrays"""
    print("\n=== Array Operations Demo ===\n")

    # Add tags
    print("1. Adding tags to product...")
    ProductRepository.collection.update_one(
        {'sku': 'LAPTOP-001'},
        {'$addToSet': {'tags': {'$each': ['business', 'portable']}}}
    )

    product = ProductRepository.get_product_by_sku('LAPTOP-001')
    print(f"   Tags: {', '.join(product['tags'])}")

    # Query by array element
    print("\n2. Finding products with 'wireless' tag...")
    wireless_products = list(ProductRepository.collection.find(
        {'tags': 'wireless'}
    ))
    print(f"   Found {len(wireless_products)} wireless products")


def demonstrate_embedded_documents():
    """Demonstrate working with embedded documents"""
    print("\n=== Embedded Documents Demo ===\n")

    # Update nested field
    print("1. Updating specifications...")
    ProductRepository.collection.update_one(
        {'sku': 'LAPTOP-001'},
        {
            '$set': {
                'specifications.display': '15.6 inch 4K',
                'specifications.weight': '1.8 kg'
            }
        }
    )

    product = ProductRepository.get_product_by_sku('LAPTOP-001')
    print("   Specifications:")
    for key, value in product['specifications'].items():
        print(f"     - {key}: {value}")


def demonstrate_bulk_operations():
    """Demonstrate bulk operations"""
    print("\n=== Bulk Operations Demo ===\n")

    print("Creating 100 products in bulk...")
    products_data = [
        {
            'sku': f'BULK-{i:03d}',
            'name': f'Product {i}',
            'description': f'Description for product {i}',
            'category': 'Bulk Category',
            'price': 10.00 + (i * 0.5),
            'stock': 100 - i,
            'tags': ['bulk', 'test']
        }
        for i in range(100)
    ]

    import time
    start = time.time()
    ProductRepository.bulk_create_products(products_data)
    elapsed = time.time() - start

    print(f"Created 100 products in {elapsed:.3f} seconds")

    # Cleanup
    result = ProductRepository.collection.delete_many({'sku': {'$regex': '^BULK-'}})
    print(f"Cleaned up {result.deleted_count} bulk products")


def cleanup():
    """Clean up test data"""
    print("\n=== Cleanup ===\n")
    ProductRepository.collection.delete_many({})
    print("All test data cleaned up")


def main():
    """Main demonstration"""
    print("=" * 60)
    print("MongoDB with Python - Complete Example")
    print("=" * 60)

    try:
        # Test connection
        client.server_info()
        logger.info("Connected to MongoDB successfully")

        # Setup
        print("\nSetting up indexes...")
        ProductRepository.setup_indexes()

        # Demonstrations
        demonstrate_crud_operations()
        demonstrate_queries()
        demonstrate_aggregations()
        demonstrate_array_operations()
        demonstrate_embedded_documents()
        demonstrate_bulk_operations()

        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)

    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise
    finally:
        # Cleanup
        cleanup()
        client.close()
        logger.info("MongoDB connection closed")


if __name__ == "__main__":
    main()
