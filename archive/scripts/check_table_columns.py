#!/usr/bin/env python3
"""
Quick script to check table column structures
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.connectors.postgresql_connector import PostgreSQLConnector
from tests.test_postgresql_smoke import TestPostgreSQLSmoke

def check_table_columns():
    # Set up smoke tester to get connection config
    smoke_tester = TestPostgreSQLSmoke()
    smoke_tester.setup_class()
    
    # Get effective configuration
    effective_config = smoke_tester._get_effective_config()
    
    if not effective_config:
        print("Could not get PostgreSQL configuration")
        return
    
    # Get credentials
    if 'username' in effective_config and 'password' in effective_config:
        username = effective_config['username']
        password = effective_config['password']
    else:
        username = os.getenv('DB_USERNAME', 'postgres')
        password = os.getenv('DB_PASSWORD', 'password')
    
    connector = PostgreSQLConnector(
        host=effective_config.get('host', 'localhost'),
        port=effective_config.get('port', 5432),
        database=effective_config.get('database', 'testdb'),
        username=username,
        password=password
    )
    
    connector.connect()
    cursor = connector.connection.cursor()

    tables = ['orders', 'new_orders', 'employees', 'new_employees']
    
    for table in tables:
        print(f'\n=== {table.upper()} TABLE COLUMNS ===')
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """, (table,))
        
        cols = cursor.fetchall()
        for col in cols:
            print(f'  {col[0]}: {col[1]}')
    
    connector.disconnect()

if __name__ == "__main__":
    check_table_columns()