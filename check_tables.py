#!/usr/bin/env python3
"""
Check what tables exist in the database
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.validators.data_validator import DataValidator

def check_database_tables():
    try:
        dv = DataValidator()
        # Get the PostgreSQL connection through the private method
        conn = dv._get_postgresql_connection()
        
        result = conn.execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        print("📋 Available Tables in Database:")
        print("-" * 40)
        
        # Handle tuple result format (success, data)
        if result and isinstance(result, tuple) and len(result) == 2:
            success, data = result
            if success and data:
                source_tables = []
                target_tables = []
                
                for row in data:
                    table_name = row[0]  # table_name is the first element
                    
                    # Get row count
                    count_result = conn.execute_query(f"SELECT COUNT(*) as cnt FROM {table_name}")
                    if count_result and isinstance(count_result, tuple) and count_result[0]:
                        row_count = count_result[1][0][0] if count_result[1] else 0
                    else:
                        row_count = 0
                    
                    print(f"   • {table_name} ({row_count} rows)")
                    
                    # Categorize tables
                    if table_name.startswith('new_'):
                        target_tables.append(table_name)
                    elif table_name in ['products', 'employees', 'orders']:
                        source_tables.append(table_name)
                
                # Analysis
                print(f"\n📊 TABLE ANALYSIS:")
                print(f"   📋 Source Tables: {source_tables}")
                print(f"   📋 Target Tables: {target_tables}")
                
                # Check for missing target tables
                expected_targets = {
                    'products': 'new_products',
                    'employees': 'new_employees', 
                    'orders': 'new_orders'
                }
                
                print(f"\n🔍 SOURCE → TARGET MAPPING:")
                for source, expected_target in expected_targets.items():
                    if source in [t for t in source_tables]:
                        if expected_target in target_tables:
                            print(f"   ✅ {source} → {expected_target}")
                        else:
                            print(f"   ❌ {source} → {expected_target} (MISSING)")
                    else:
                        print(f"   ⚠️  {source} (SOURCE MISSING)")
            else:
                print("   Query failed or returned no data")
        else:
            print("   Unexpected result format")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_tables()