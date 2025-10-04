#!/usr/bin/env python3
"""
Generate SQL statements to create inconsistent test data
This approach creates SQL that can be run manually or through psql
"""

def generate_inconsistent_data_sql():
    """Generate SQL statements to create test data with quality issues"""
    
    print("🔧 SQL STATEMENTS TO CREATE INCONSISTENT TEST DATA")
    print("=" * 70)
    print("Copy and run these SQL statements in your PostgreSQL database:")
    print()
    
    print("-- 1. ADD DUPLICATE PRODUCT RECORDS")
    print("INSERT INTO new_products (product_name, category_id, price, stock_quantity, product_description, created_at, last_updated)")
    print("VALUES ")
    print("    ('Duplicate Test Product', 1, 99.99, 10, 'First duplicate', NOW(), NOW()),")
    print("    ('Duplicate Test Product', 1, 89.99, 15, 'Second duplicate', NOW(), NOW()),")
    print("    ('Another Duplicate Item', 2, 199.99, 5, 'Third duplicate', NOW(), NOW()),")
    print("    ('Another Duplicate Item', 2, 179.99, 8, 'Fourth duplicate', NOW(), NOW()),")
    print("    ('Triple Duplicate', 1, 50.00, 10, 'First triple', NOW(), NOW()),")
    print("    ('Triple Duplicate', 1, 55.00, 12, 'Second triple', NOW(), NOW()),")
    print("    ('Triple Duplicate', 1, 45.00, 8, 'Third triple', NOW(), NOW());")
    print()
    
    print("-- 2. ADD PRODUCTS WITH INVALID PRICES")
    print("INSERT INTO new_products (product_name, category_id, price, stock_quantity, product_description, created_at, last_updated)")
    print("VALUES ")
    print("    ('Negative Price Product', 1, -50.00, 10, 'This has negative price', NOW(), NOW()),")
    print("    ('Zero Price Product', 2, 0.00, 5, 'This has zero price', NOW(), NOW()),")
    print("    ('Extremely Negative Price', 1, -999.99, 3, 'Very negative price', NOW(), NOW());")
    print()
    
    print("-- 3. ADD EMPLOYEES WITH INVALID SALARIES")
    print("INSERT INTO new_employees (first_name, last_name, email, phone_number, department_id, salary, middle_name, is_active, created_at)")
    print("VALUES ")
    print("    ('John', 'NegativeSalary', 'john.negative@test.com', '555-0001', 1, -25000.00, NULL, true, NOW()),")
    print("    ('Jane', 'ZeroSalary', 'jane.zero@test.com', '555-0002', 2, 0.00, NULL, true, NOW()),")
    print("    ('Bob', 'HugeSalary', 'bob.huge@test.com', '555-0003', 1, -50000.00, NULL, true, NOW());")
    print()
    
    print("-- 4. ADD ORDERS WITH MISSING ORDER DATES")
    print("INSERT INTO new_orders (customer_id, employee_id, order_date, required_date, shipped_date, ship_via, freight, order_total, created_at)")
    print("VALUES ")
    print("    (1, 1, NULL, NOW() + interval '7 days', NULL, 1, 10.00, 100.00, NOW()),")
    print("    (2, 2, NULL, NOW() + interval '5 days', NULL, 2, 15.00, 200.00, NOW()),")
    print("    (3, 1, NULL, NOW() + interval '10 days', NULL, 1, 20.00, 150.00, NOW());")
    print()
    
    print("-- 5. ADD ORDERS WITH INVALID EMPLOYEE REFERENCES")
    print("INSERT INTO new_orders (customer_id, employee_id, order_date, required_date, shipped_date, ship_via, freight, order_total, created_at)")
    print("VALUES ")
    print("    (1, 9999, NOW(), NOW() + interval '7 days', NULL, 1, 10.00, 150.00, NOW()),")
    print("    (2, 8888, NOW(), NOW() + interval '5 days', NULL, 2, 20.00, 250.00, NOW()),")
    print("    (3, 7777, NOW(), NOW() + interval '3 days', NULL, 1, 30.00, 300.00, NOW()),")
    print("    (1, 6666, NOW(), NOW() + interval '14 days', NULL, 2, 25.00, 175.00, NOW());")
    print()
    
    print("-- 6. ADD MORE COMPLEX DUPLICATES")
    print("INSERT INTO new_products (product_name, category_id, price, stock_quantity, product_description, created_at, last_updated)")
    print("VALUES ")
    print("    ('Complex Duplicate', 1, 100.00, 20, 'First complex', NOW(), NOW()),")
    print("    ('Complex Duplicate', 2, 110.00, 15, 'Second complex', NOW(), NOW()),")
    print("    ('Complex Duplicate', 1, 95.00, 25, 'Third complex', NOW(), NOW()),")
    print("    ('Simple Dup', 2, 75.00, 5, 'First simple', NOW(), NOW()),")
    print("    ('Simple Dup', 2, 80.00, 8, 'Second simple', NOW(), NOW());")
    print()
    
    print("=" * 70)
    print("🎯 SUMMARY OF QUALITY ISSUES THAT WILL BE CREATED:")
    print("   🔴 12 duplicate product records (same product_name)")
    print("   🔴 3 products with negative/zero prices")
    print("   🔴 3 employees with invalid salaries (negative/zero)")
    print("   🔴 3 orders missing order_date (NULL values)")
    print("   🔴 4 orders with invalid employee_id references (orphaned)")
    print()
    print("After running these SQL statements, execute:")
    print("   python test_data_quality_reporting.py")
    print("Or:")
    print("   python execute_enhanced_data_validation_tests.py enhanced_unified_sdm_test_suite.xlsx")
    print()
    print("This will trigger the enhanced data quality validation reporting!")

def generate_sql_file():
    """Create a SQL file that can be executed directly"""
    
    sql_content = """-- ================================================================
-- INCONSISTENT TEST DATA FOR DATA QUALITY VALIDATION TESTING
-- ================================================================
-- This SQL creates data with known quality issues to demonstrate
-- the enhanced data quality validation reporting capabilities
-- ================================================================

-- 1. ADD DUPLICATE PRODUCT RECORDS
INSERT INTO new_products (product_name, category_id, price, stock_quantity, product_description, created_at, last_updated)
VALUES 
    ('Duplicate Test Product', 1, 99.99, 10, 'First duplicate', NOW(), NOW()),
    ('Duplicate Test Product', 1, 89.99, 15, 'Second duplicate', NOW(), NOW()),
    ('Another Duplicate Item', 2, 199.99, 5, 'Third duplicate', NOW(), NOW()),
    ('Another Duplicate Item', 2, 179.99, 8, 'Fourth duplicate', NOW(), NOW()),
    ('Triple Duplicate', 1, 50.00, 10, 'First triple', NOW(), NOW()),
    ('Triple Duplicate', 1, 55.00, 12, 'Second triple', NOW(), NOW()),
    ('Triple Duplicate', 1, 45.00, 8, 'Third triple', NOW(), NOW());

-- 2. ADD PRODUCTS WITH INVALID PRICES
INSERT INTO new_products (product_name, category_id, price, stock_quantity, product_description, created_at, last_updated)
VALUES 
    ('Negative Price Product', 1, -50.00, 10, 'This has negative price', NOW(), NOW()),
    ('Zero Price Product', 2, 0.00, 5, 'This has zero price', NOW(), NOW()),
    ('Extremely Negative Price', 1, -999.99, 3, 'Very negative price', NOW(), NOW());

-- 3. ADD EMPLOYEES WITH INVALID SALARIES
INSERT INTO new_employees (first_name, last_name, email, phone_number, department_id, salary, middle_name, is_active, created_at)
VALUES 
    ('John', 'NegativeSalary', 'john.negative@test.com', '555-0001', 1, -25000.00, NULL, true, NOW()),
    ('Jane', 'ZeroSalary', 'jane.zero@test.com', '555-0002', 2, 0.00, NULL, true, NOW()),
    ('Bob', 'HugeSalary', 'bob.huge@test.com', '555-0003', 1, -50000.00, NULL, true, NOW());

-- 4. ADD ORDERS WITH MISSING ORDER DATES
INSERT INTO new_orders (customer_id, employee_id, order_date, required_date, shipped_date, ship_via, freight, order_total, created_at)
VALUES 
    (1, 1, NULL, NOW() + interval '7 days', NULL, 1, 10.00, 100.00, NOW()),
    (2, 2, NULL, NOW() + interval '5 days', NULL, 2, 15.00, 200.00, NOW()),
    (3, 1, NULL, NOW() + interval '10 days', NULL, 1, 20.00, 150.00, NOW());

-- 5. ADD ORDERS WITH INVALID EMPLOYEE REFERENCES
INSERT INTO new_orders (customer_id, employee_id, order_date, required_date, shipped_date, ship_via, freight, order_total, created_at)
VALUES 
    (1, 9999, NOW(), NOW() + interval '7 days', NULL, 1, 10.00, 150.00, NOW()),
    (2, 8888, NOW(), NOW() + interval '5 days', NULL, 2, 20.00, 250.00, NOW()),
    (3, 7777, NOW(), NOW() + interval '3 days', NULL, 1, 30.00, 300.00, NOW()),
    (1, 6666, NOW(), NOW() + interval '14 days', NULL, 2, 25.00, 175.00, NOW());

-- 6. ADD MORE COMPLEX DUPLICATES
INSERT INTO new_products (product_name, category_id, price, stock_quantity, product_description, created_at, last_updated)
VALUES 
    ('Complex Duplicate', 1, 100.00, 20, 'First complex', NOW(), NOW()),
    ('Complex Duplicate', 2, 110.00, 15, 'Second complex', NOW(), NOW()),
    ('Complex Duplicate', 1, 95.00, 25, 'Third complex', NOW(), NOW()),
    ('Simple Dup', 2, 75.00, 5, 'First simple', NOW(), NOW()),
    ('Simple Dup', 2, 80.00, 8, 'Second simple', NOW(), NOW());

-- ================================================================
-- SUMMARY OF QUALITY ISSUES CREATED:
-- ================================================================
-- 🔴 12 duplicate product records (same product_name)
-- 🔴 3 products with negative/zero prices  
-- 🔴 3 employees with invalid salaries (negative/zero)
-- 🔴 3 orders missing order_date (NULL values)
-- 🔴 4 orders with invalid employee_id references (orphaned)
-- ================================================================

-- After running this SQL, execute:
-- python test_data_quality_reporting.py
-- OR
-- python execute_enhanced_data_validation_tests.py enhanced_unified_sdm_test_suite.xlsx
-- 
-- This will trigger the enhanced data quality validation reporting!
"""
    
    with open('create_inconsistent_data.sql', 'w') as f:
        f.write(sql_content)
    
    print("📄 Created file: create_inconsistent_data.sql")
    print("You can run this SQL file using:")
    print("   psql -h localhost -U postgres -d your_database -f create_inconsistent_data.sql")

if __name__ == "__main__":
    generate_inconsistent_data_sql()
    print()
    generate_sql_file()