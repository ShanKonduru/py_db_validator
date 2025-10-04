-- =============================================================================
-- Data Validation Target Tables Creation Script
-- =============================================================================
-- This script creates target tables for advanced data validation testing
-- These tables are designed to be similar to source tables but with some
-- intentional variations for testing schema, data type, and constraint differences
-- =============================================================================

-- Drop tables if they exist (for recreation)
DROP TABLE IF EXISTS public.new_orders CASCADE;
DROP TABLE IF EXISTS public.new_employees CASCADE;
DROP TABLE IF EXISTS public.new_products CASCADE;

-- =============================================================================
-- CREATE new_products table (target for products validation)
-- =============================================================================
-- Intentional variations from source:
-- 1. product_description length changed from 500 to 1000 (schema difference)
-- 2. Added new column 'last_updated' for testing extra columns
-- 3. Changed some data types slightly for testing
-- =============================================================================

CREATE TABLE public.new_products (
    product_id INTEGER NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category_id INTEGER,
    price DECIMAL(12,2),  -- Changed precision from (10,2) to (12,2)
    stock_quantity INTEGER DEFAULT 0,
    product_description VARCHAR(1000),  -- Changed from 500 to 1000
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- New column
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT pk_new_products PRIMARY KEY (product_id)
);

-- Create index for performance
CREATE INDEX idx_new_products_category ON public.new_products(category_id);
CREATE INDEX idx_new_products_name ON public.new_products(product_name);

-- Insert sample data with some variations
INSERT INTO public.new_products (product_id, product_name, category_id, price, stock_quantity, product_description, is_active) VALUES
(1, 'Laptop Computer', 1, 899.99, 25, 'High-performance laptop for business use', true),
(2, 'Wireless Mouse', 2, 29.99, 150, 'Ergonomic wireless mouse with USB receiver', true),
(3, 'USB Keyboard', 2, 49.99, 75, 'Mechanical keyboard with backlight', true),
(4, 'Monitor 24inch', 3, 299.99, 30, '24-inch LED monitor with HDMI connectivity', true),
(5, 'External Hard Drive', 4, 89.99, 40, '1TB external storage device', true),
-- Add some records with NULL values for testing
(6, 'Premium Headphones', NULL, 199.99, NULL, 'Noise-canceling wireless headphones', true),
(7, 'Tablet Device', 5, NULL, 20, 'Android tablet with 10-inch display', true),
(8, 'Smart Phone', 6, 699.99, 0, NULL, false);  -- Inactive product

-- =============================================================================
-- CREATE new_employees table (target for employees validation)
-- =============================================================================
-- Intentional variations from source:
-- 1. phone_number length changed from 20 to 15 (schema difference)
-- 2. Added 'middle_name' column for testing extra columns
-- 3. Changed salary to NUMERIC instead of DECIMAL for testing
-- =============================================================================

CREATE TABLE public.new_employees (
    employee_id INTEGER NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),  -- New column
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(15),  -- Changed from 20 to 15
    hire_date DATE NOT NULL,
    salary NUMERIC(12,2),  -- Changed from DECIMAL to NUMERIC
    department_id INTEGER,
    manager_id INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_new_employees PRIMARY KEY (employee_id)
);

-- Create indexes
CREATE INDEX idx_new_employees_dept ON public.new_employees(department_id);
CREATE INDEX idx_new_employees_manager ON public.new_employees(manager_id);
CREATE INDEX idx_new_employees_email ON public.new_employees(email);

-- Insert sample data with variations
INSERT INTO public.new_employees (employee_id, first_name, middle_name, last_name, email, phone_number, hire_date, salary, department_id, manager_id, is_active) VALUES
(1, 'John', 'Michael', 'Smith', 'john.smith@company.com', '555-0101', '2023-01-15', 75000.00, 1, NULL, true),
(2, 'Sarah', NULL, 'Johnson', 'sarah.johnson@company.com', '555-0102', '2023-02-01', 68000.00, 2, 1, true),
(3, 'Mike', 'Robert', 'Brown', 'mike.brown@company.com', '555-0103', '2023-03-01', 72000.00, 1, 1, true),
(4, 'Lisa', 'Ann', 'Davis', 'lisa.davis@company.com', NULL, '2023-04-01', 65000.00, 3, 1, true),  -- NULL phone
(5, 'David', NULL, 'Wilson', 'david.wilson@company.com', '555-0105', '2023-05-01', NULL, 2, 2, true),  -- NULL salary
-- Some inactive employees
(6, 'Jennifer', 'Marie', 'Taylor', 'jennifer.taylor@company.com', '555-0106', '2022-06-01', 70000.00, 1, 1, false),
(7, 'Robert', 'James', 'Anderson', NULL, '555-0107', '2022-07-01', 66000.00, 3, 1, false);  -- NULL email

-- =============================================================================
-- CREATE new_orders table (target for orders validation)
-- =============================================================================
-- Intentional variations from source:
-- 1. Changed order_total precision from (10,2) to (15,2)
-- 2. Added 'shipping_address' column for testing extra columns
-- 3. Added 'order_status' enum-like field
-- =============================================================================

CREATE TABLE public.new_orders (
    order_id INTEGER NOT NULL,
    customer_id INTEGER,
    employee_id INTEGER,
    order_date DATE NOT NULL,
    required_date DATE,
    shipped_date DATE,
    ship_via INTEGER,
    freight DECIMAL(8,2),
    order_total DECIMAL(15,2),  -- Changed precision from (10,2) to (15,2)
    shipping_address TEXT,  -- New column
    order_status VARCHAR(20) DEFAULT 'PENDING',  -- New column
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_new_orders PRIMARY KEY (order_id)
);

-- Create indexes
CREATE INDEX idx_new_orders_customer ON public.new_orders(customer_id);
CREATE INDEX idx_new_orders_employee ON public.new_orders(employee_id);
CREATE INDEX idx_new_orders_date ON public.new_orders(order_date);
CREATE INDEX idx_new_orders_status ON public.new_orders(order_status);

-- Insert sample data with variations
INSERT INTO public.new_orders (order_id, customer_id, employee_id, order_date, required_date, shipped_date, ship_via, freight, order_total, shipping_address, order_status) VALUES
(1, 101, 1, '2024-01-10', '2024-01-15', '2024-01-12', 1, 15.50, 1299.99, '123 Main St, City, State 12345', 'SHIPPED'),
(2, 102, 2, '2024-01-11', '2024-01-16', NULL, 2, 25.75, 899.98, '456 Oak Ave, City, State 12346', 'PENDING'),  -- NULL shipped_date
(3, 103, 1, '2024-01-12', '2024-01-17', '2024-01-14', 1, 12.00, 149.99, NULL, 'SHIPPED'),  -- NULL shipping_address
(4, 104, 3, '2024-01-13', NULL, NULL, 3, 35.00, 2199.97, '789 Pine St, City, State 12347', 'PROCESSING'),  -- NULL required_date
(5, 105, 2, '2024-01-14', '2024-01-19', '2024-01-16', 2, NULL, 499.99, '321 Elm St, City, State 12348', 'SHIPPED'),  -- NULL freight
(6, 106, 1, '2024-01-15', '2024-01-20', NULL, 1, 18.25, NULL, '654 Maple Dr, City, State 12349', 'CANCELLED'),  -- NULL order_total
(7, NULL, 3, '2024-01-16', '2024-01-21', NULL, 2, 22.50, 799.99, '987 Cedar Ln, City, State 12350', 'PENDING');  -- NULL customer_id

-- =============================================================================
-- Create some additional validation helper tables
-- =============================================================================

-- Table for storing validation results (optional)
CREATE TABLE IF NOT EXISTS public.validation_results (
    validation_id SERIAL PRIMARY KEY,
    test_case_id VARCHAR(50),
    source_table VARCHAR(100),
    target_table VARCHAR(100),
    validation_type VARCHAR(50),
    validation_status VARCHAR(20),
    error_message TEXT,
    validation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- Grant permissions (adjust as needed for your environment)
-- =============================================================================

-- Grant permissions to public schema (adjust user/role as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON public.new_products TO your_application_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON public.new_employees TO your_application_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON public.new_orders TO your_application_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON public.validation_results TO your_application_user;

-- =============================================================================
-- Verification Queries
-- =============================================================================

-- Verify table creation and data
SELECT 'new_products' as table_name, COUNT(*) as row_count FROM public.new_products
UNION ALL
SELECT 'new_employees' as table_name, COUNT(*) as row_count FROM public.new_employees  
UNION ALL
SELECT 'new_orders' as table_name, COUNT(*) as row_count FROM public.new_orders;

-- Show schema differences for validation testing
SELECT 
    table_name,
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name IN ('new_products', 'new_employees', 'new_orders')
ORDER BY table_name, ordinal_position;

-- =============================================================================
-- Notes for Data Validation Testing:
-- =============================================================================
-- 1. Schema Validation: Compare column names, data types, constraints between source and target
-- 2. Row Count Validation: Compare COUNT(*) between source and target tables
-- 3. NULL Value Validation: Compare NULL patterns column by column
-- 4. Data Quality: Compare ranges, patterns, and data distribution
-- 
-- Example validation scenarios included:
-- - Extra columns in target (middle_name, last_updated, shipping_address, order_status)
-- - Different data type precision (price, order_total) 
-- - Different VARCHAR lengths (product_description, phone_number)
-- - NULL values in various patterns for comprehensive testing
-- - Data type changes (DECIMAL vs NUMERIC)
-- =============================================================================

COMMIT;