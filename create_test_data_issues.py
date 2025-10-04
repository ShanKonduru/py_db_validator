#!/usr/bin/env python3
"""
Create test data with quality issues to demonstrate enhanced reporting
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.connectors.postgresql_connector import PostgreSQLConnector

def create_problematic_test_data():
    """Insert data with known quality issues for testing"""
    
    print("🔧 CREATING TEST DATA WITH QUALITY ISSUES")
    print("=" * 60)
    
    # Connect to PostgreSQL using configuration
    from src.config.db_config import get_db_config
    
    config = get_db_config()
    connector = PostgreSQLConnector(
        host=config['host'],
        port=config['port'], 
        username=config['username'],
        password=config['password'],
        database=config['database']
    )
    connector.connect()
    cursor = connector.connection.cursor()
    
    try:
        # 1. Insert duplicate records in new_products
        print("1. Inserting duplicate product records...")
        cursor.execute("""
            INSERT INTO new_products (product_name, category_id, price, stock_quantity, product_description, created_at, last_updated)
            VALUES 
            ('Duplicate Product', 1, 99.99, 10, 'Test product 1', NOW(), NOW()),
            ('Duplicate Product', 1, 99.99, 15, 'Test product 2', NOW(), NOW()),
            ('Another Duplicate', 2, 149.99, 5, 'Test product 3', NOW(), NOW()),
            ('Another Duplicate', 2, 149.99, 8, 'Test product 4', NOW(), NOW())
        """)
        
        # 2. Insert products with negative prices
        print("2. Inserting products with invalid prices...")
        cursor.execute("""
            INSERT INTO new_products (product_name, category_id, price, stock_quantity, product_description, created_at, last_updated)
            VALUES 
            ('Invalid Price Product 1', 1, -50.00, 10, 'Negative price test', NOW(), NOW()),
            ('Invalid Price Product 2', 2, -25.99, 5, 'Another negative price', NOW(), NOW())
        """)
        
        # 3. Insert employees with invalid salaries
        print("3. Inserting employees with invalid salaries...")
        cursor.execute("""
            INSERT INTO new_employees (first_name, last_name, email, phone_number, department_id, salary, middle_name, is_active, created_at)
            VALUES 
            ('John', 'InvalidSalary', 'john.invalid@example.com', '123-456-7890', 1, -5000.00, NULL, true, NOW()),
            ('Jane', 'ZeroSalary', 'jane.zero@example.com', '123-456-7891', 2, 0.00, NULL, true, NOW())
        """)
        
        # 4. Insert orders with missing critical data
        print("4. Inserting orders with missing order_date...")
        cursor.execute("""
            INSERT INTO new_orders (customer_id, employee_id, required_date, shipped_date, ship_via, freight, order_total, created_at)
            VALUES 
            (1, 1, NULL, NULL, 1, 10.00, 100.00, NOW()),
            (2, 2, NULL, NULL, 2, 15.00, 200.00, NOW())
        """)
        
        # 5. Insert orders with invalid employee_id (orphaned records)
        print("5. Inserting orders with invalid employee references...")
        cursor.execute("""
            INSERT INTO new_orders (customer_id, employee_id, order_date, required_date, shipped_date, ship_via, freight, order_total, created_at)
            VALUES 
            (1, 9999, NOW(), NOW() + interval '7 days', NULL, 1, 10.00, 150.00, NOW()),
            (2, 8888, NOW(), NOW() + interval '5 days', NULL, 2, 20.00, 250.00, NOW())
        """)
        
        connector.connection.commit()
        print("✅ Test data with quality issues created successfully!")
        
        # Show record counts
        cursor.execute("SELECT COUNT(*) FROM new_products")
        products_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM new_employees") 
        employees_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM new_orders")
        orders_count = cursor.fetchone()[0]
        
        print(f"📊 Current record counts:")
        print(f"   new_products: {products_count} records")
        print(f"   new_employees: {employees_count} records") 
        print(f"   new_orders: {orders_count} records")
        
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        connector.connection.rollback()
    
    finally:
        connector.disconnect()

if __name__ == "__main__":
    create_problematic_test_data()