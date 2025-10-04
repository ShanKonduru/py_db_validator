-- SQLite version of target tables for data validation testing
-- These tables have intentional deviations from source tables to test validation scenarios

-- Drop tables if they exist
DROP TABLE IF EXISTS new_products;
DROP TABLE IF EXISTS new_employees;
DROP TABLE IF EXISTS new_orders;

-- Create new_products table (with intentional schema deviations)
CREATE TABLE new_products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,  -- Changed from VARCHAR(255) to TEXT
    category TEXT,      -- Changed from VARCHAR(100) to TEXT
    price REAL,         -- Changed from DECIMAL(10,2) to REAL
    stock_quantity INTEGER,
    is_active INTEGER,  -- Changed from BOOLEAN to INTEGER (SQLite boolean)
    created_date TEXT,  -- Changed from DATE to TEXT
    description TEXT,   -- New column not in source
    last_updated TEXT   -- Changed from TIMESTAMP to TEXT
);

-- Create new_employees table (with intentional deviations)
CREATE TABLE new_employees (
    employee_id INTEGER PRIMARY KEY,
    first_name TEXT,     -- Changed from VARCHAR(50) to TEXT
    last_name TEXT,      -- Changed from VARCHAR(50) to TEXT
    email TEXT,          -- Changed from VARCHAR(100) to TEXT
    phone TEXT,          -- Changed from VARCHAR(20) to TEXT
    department TEXT,     -- Changed from VARCHAR(50) to TEXT
    salary REAL,         -- Changed from DECIMAL(12,2) to REAL
    hire_date TEXT,      -- Changed from DATE to TEXT
    is_active INTEGER,   -- Changed from BOOLEAN to INTEGER
    manager_id INTEGER,
    address TEXT,        -- New column not in source
    city TEXT,           -- New column not in source
    FOREIGN KEY (manager_id) REFERENCES new_employees(employee_id)
);

-- Create new_orders table (with intentional deviations)
CREATE TABLE new_orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    employee_id INTEGER,
    order_date TEXT,     -- Changed from DATE to TEXT
    ship_date TEXT,      -- Changed from DATE to TEXT
    total_amount REAL,   -- Changed from DECIMAL(15,2) to REAL
    status TEXT,         -- Changed from VARCHAR(20) to TEXT
    payment_method TEXT, -- New column not in source
    notes TEXT,          -- New column not in source
    FOREIGN KEY (employee_id) REFERENCES new_employees(employee_id)
);

-- Insert sample data with intentional deviations for testing

-- Products data (some with NULL values and different data patterns)
INSERT INTO new_products (product_id, product_name, category, price, stock_quantity, is_active, created_date, description, last_updated) VALUES
(1, 'Laptop Pro', 'Electronics', 1299.99, 50, 1, '2024-01-15', 'High-performance laptop', '2024-01-15 10:00:00'),
(2, 'Wireless Mouse', 'Electronics', 29.99, 100, 1, '2024-01-16', 'Ergonomic wireless mouse', '2024-01-16 11:30:00'),
(3, 'Office Chair', 'Furniture', 199.99, 25, 1, '2024-01-17', 'Comfortable office chair', '2024-01-17 09:15:00'),
(4, NULL, 'Electronics', 89.99, 0, 0, '2024-01-18', NULL, '2024-01-18 14:20:00'),  -- NULL product name
(5, 'Standing Desk', 'Furniture', 449.99, 15, 1, '2024-01-19', 'Adjustable standing desk', '2024-01-19 16:45:00'),
(6, 'USB Cable', 'Electronics', 12.99, 200, 1, '2024-01-20', 'USB-C to USB-A cable', '2024-01-20 08:30:00'),
(7, 'Monitor Stand', 'Electronics', 39.99, 75, 1, '2024-01-21', 'Adjustable monitor stand', '2024-01-21 13:10:00'),
(8, 'Desk Lamp', 'Furniture', 69.99, 40, 1, '2024-01-22', 'LED desk lamp', '2024-01-22 15:25:00');

-- Employees data (some with NULL values and missing records)
INSERT INTO new_employees (employee_id, first_name, last_name, email, phone, department, salary, hire_date, is_active, manager_id, address, city) VALUES
(1, 'John', 'Smith', 'john.smith@company.com', '555-0101', 'IT', 75000.00, '2023-01-15', 1, NULL, '123 Main St', 'New York'),
(2, 'Jane', 'Doe', 'jane.doe@company.com', '555-0102', 'HR', 65000.00, '2023-02-01', 1, 1, '456 Oak Ave', 'Boston'),
(3, 'Bob', 'Johnson', 'bob.johnson@company.com', '555-0103', 'Finance', 70000.00, '2023-03-15', 1, 1, '789 Pine St', 'Chicago'),
(4, NULL, 'Wilson', 'wilson@company.com', NULL, 'IT', 68000.00, '2023-04-01', 0, 1, NULL, 'Seattle'),  -- NULL first name and phone
(5, 'Alice', 'Brown', 'alice.brown@company.com', '555-0105', 'Marketing', 62000.00, '2023-05-15', 1, 1, '321 Elm St', 'Denver');
-- Note: Missing employee_id 6 that might exist in source - intentional row count difference

-- Orders data (some with NULL values and extra records)
INSERT INTO new_orders (order_id, customer_id, employee_id, order_date, ship_date, total_amount, status, payment_method, notes) VALUES
(1, 101, 1, '2024-01-10', '2024-01-12', 1329.98, 'Completed', 'Credit Card', 'Rush order'),
(2, 102, 2, '2024-01-11', '2024-01-13', 229.98, 'Completed', 'PayPal', NULL),
(3, 103, 3, '2024-01-12', NULL, 89.99, 'Processing', 'Credit Card', 'Customer requested delay'),  -- NULL ship_date
(4, 104, 1, '2024-01-13', '2024-01-15', 462.98, 'Completed', 'Bank Transfer', NULL),
(5, 105, 2, '2024-01-14', '2024-01-16', 52.98, 'Shipped', 'Credit Card', NULL),
(6, NULL, 3, '2024-01-15', '2024-01-17', 109.98, 'Completed', NULL, 'Anonymous order'),  -- NULL customer_id and payment_method
(7, 107, NULL, '2024-01-16', '2024-01-18', 69.99, 'Completed', 'Credit Card', NULL);  -- NULL employee_id

-- Create indexes for better performance (different from source)
CREATE INDEX idx_new_products_category ON new_products(category);
CREATE INDEX idx_new_products_active ON new_products(is_active);
CREATE INDEX idx_new_employees_dept ON new_employees(department);
CREATE INDEX idx_new_employees_active ON new_employees(is_active);
CREATE INDEX idx_new_orders_customer ON new_orders(customer_id);
CREATE INDEX idx_new_orders_status ON new_orders(status);

-- Summary of intentional deviations for testing:
-- 1. Schema differences: Data types changed (VARCHAR to TEXT, DECIMAL to REAL, etc.)
-- 2. Extra columns: description in products, address/city in employees, payment_method/notes in orders
-- 3. NULL values: Various NULL entries that might not exist in source
-- 4. Row count differences: Missing employee_id 6, extra order records
-- 5. Data quality issues: NULL names, missing foreign key references