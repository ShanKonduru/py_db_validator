#!/usr/bin/env python3
"""
Create inconsistent test data to demonstrate enhanced data quality validation
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.connectors.postgresql_connector import PostgreSQLConnector
from tests.test_postgresql_smoke import TestPostgreSQLSmoke

def get_db_connection():
    """Get database connection using the same configuration as the working tests"""
    try:
        # Use the same approach as the data validator
        smoke_tester = TestPostgreSQLSmoke()
        smoke_tester.setup_class()
        
        # Get effective configuration
        effective_config = smoke_tester._get_effective_config()
        
        if not effective_config:
            raise Exception("Could not get PostgreSQL configuration")
        
        # Get credentials
        if 'username' in effective_config and 'password' in effective_config:
            username = effective_config['username']
            password = effective_config['password']
            host = effective_config.get('host', 'localhost')
            port = effective_config.get('port', 5432)
            database = effective_config.get('database', 'postgres')
        else:
            raise Exception("Database credentials not found in configuration")
        
        # Create connector
        connector = PostgreSQLConnector(host, port, username, password, database)
        connector.connect()
        
        return connector.connection
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("Please ensure PostgreSQL is running and credentials are correct")
        return None

def create_inconsistent_data():
    """Create test data with known quality issues"""
    
    print("🔧 CREATING INCONSISTENT TEST DATA FOR QUALITY VALIDATION")
    print("=" * 70)
    
    conn = get_db_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        print("📊 Current table status:")
        
        # Check current counts
        for table in ['new_products', 'new_employees', 'new_orders']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} records")
        
        print("\n🚀 Adding problematic data...")
        
        # 1. Add duplicate products (same product_name)
        print("1. Adding duplicate product records...")
        cursor.execute("""
            INSERT INTO new_products (product_name, category_id, price, stock_quantity, product_description, created_at, last_updated)
            VALUES 
            ('Duplicate Test Product', 1, 99.99, 10, 'First duplicate', NOW(), NOW()),
            ('Duplicate Test Product', 1, 89.99, 15, 'Second duplicate', NOW(), NOW()),
            ('Another Duplicate Item', 2, 199.99, 5, 'Third duplicate', NOW(), NOW()),
            ('Another Duplicate Item', 2, 179.99, 8, 'Fourth duplicate', NOW(), NOW()),
            ('Triple Duplicate', 1, 50.00, 10, 'First triple', NOW(), NOW()),
            ('Triple Duplicate', 1, 55.00, 12, 'Second triple', NOW(), NOW()),
            ('Triple Duplicate', 1, 45.00, 8, 'Third triple', NOW(), NOW())
        """)
        print("   ✅ Added 7 duplicate product records")
        
        # 2. Add products with negative/invalid prices
        print("2. Adding products with invalid prices...")
        cursor.execute("""
            INSERT INTO new_products (product_name, category_id, price, stock_quantity, product_description, created_at, last_updated)
            VALUES 
            ('Negative Price Product', 1, -50.00, 10, 'This has negative price', NOW(), NOW()),
            ('Zero Price Product', 2, 0.00, 5, 'This has zero price', NOW(), NOW()),
            ('Extremely Negative Price', 1, -999.99, 3, 'Very negative price', NOW(), NOW())
        """)
        print("   ✅ Added 3 products with invalid prices")
        
        # 3. Add employees with invalid salaries
        print("3. Adding employees with invalid salaries...")
        cursor.execute("""
            INSERT INTO new_employees (first_name, last_name, email, phone_number, department_id, salary, middle_name, is_active, created_at)
            VALUES 
            ('John', 'NegativeSalary', 'john.negative@test.com', '555-0001', 1, -25000.00, NULL, true, NOW()),
            ('Jane', 'ZeroSalary', 'jane.zero@test.com', '555-0002', 2, 0.00, NULL, true, NOW()),
            ('Bob', 'HugeSalary', 'bob.huge@test.com', '555-0003', 1, -50000.00, NULL, true, NOW())
        """)
        print("   ✅ Added 3 employees with invalid salaries")
        
        # 4. Add orders with missing critical data (NULL order_date)
        print("4. Adding orders with missing order dates...")
        cursor.execute("""
            INSERT INTO new_orders (customer_id, employee_id, order_date, required_date, shipped_date, ship_via, freight, order_total, created_at)
            VALUES 
            (1, 1, NULL, NOW() + interval '7 days', NULL, 1, 10.00, 100.00, NOW()),
            (2, 2, NULL, NOW() + interval '5 days', NULL, 2, 15.00, 200.00, NOW()),
            (3, 1, NULL, NOW() + interval '10 days', NULL, 1, 20.00, 150.00, NOW())
        """)
        print("   ✅ Added 3 orders with missing order_date")
        
        # 5. Add orders with invalid employee_id (orphaned records)
        print("5. Adding orders with invalid employee references...")
        cursor.execute("""
            INSERT INTO new_orders (customer_id, employee_id, order_date, required_date, shipped_date, ship_via, freight, order_total, created_at)
            VALUES 
            (1, 9999, NOW(), NOW() + interval '7 days', NULL, 1, 10.00, 150.00, NOW()),
            (2, 8888, NOW(), NOW() + interval '5 days', NULL, 2, 20.00, 250.00, NOW()),
            (3, 7777, NOW(), NOW() + interval '3 days', NULL, 1, 30.00, 300.00, NOW()),
            (1, 6666, NOW(), NOW() + interval '14 days', NULL, 2, 25.00, 175.00, NOW())
        """)
        print("   ✅ Added 4 orders with invalid employee_id references")
        
        # 6. Add more duplicate products with different data
        print("6. Adding more complex duplicates...")
        cursor.execute("""
            INSERT INTO new_products (product_name, category_id, price, stock_quantity, product_description, created_at, last_updated)
            VALUES 
            ('Complex Duplicate', 1, 100.00, 20, 'First complex', NOW(), NOW()),
            ('Complex Duplicate', 2, 110.00, 15, 'Second complex', NOW(), NOW()),
            ('Complex Duplicate', 1, 95.00, 25, 'Third complex', NOW(), NOW()),
            ('Simple Dup', 2, 75.00, 5, 'First simple', NOW(), NOW()),
            ('Simple Dup', 2, 80.00, 8, 'Second simple', NOW(), NOW())
        """)
        print("   ✅ Added 5 more duplicate products")
        
        conn.commit()
        
        print("\n📊 Updated table status:")
        for table in ['new_products', 'new_employees', 'new_orders']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} records")
        
        print("\n✅ INCONSISTENT TEST DATA CREATED SUCCESSFULLY!")
        print("\nData quality issues added:")
        print("  🔴 12 duplicate product records")
        print("  🔴 3 products with negative/zero prices")
        print("  🔴 3 employees with invalid salaries")
        print("  🔴 3 orders missing order_date")
        print("  🔴 4 orders with invalid employee_id references")
        print("\n🚀 Now run the data quality validation to see the enhanced reporting!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating inconsistent data: {str(e)}")
        conn.rollback()
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = create_inconsistent_data()
    if success:
        print("\n🎯 Next steps:")
        print("   Run: python test_data_quality_reporting.py")
        print("   Or:  python execute_enhanced_data_validation_tests.py enhanced_unified_sdm_test_suite.xlsx")
    else:
        print("\n❌ Failed to create test data. Check database connection.")