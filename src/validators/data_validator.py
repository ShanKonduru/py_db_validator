"""
Data Validation Module
Provides functions for comparing source and target databases to validate data integrity,
schema compliance, and data quality using PostgreSQL.
"""

import os
import sys
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.connectors.postgresql_connector import PostgreSQLConnector
from tests.test_postgresql_smoke import TestPostgreSQLSmoke


@dataclass
class ValidationResult:
    """Result of a data validation check"""
    passed: bool
    message: str
    details: Dict[str, Any] = None


class DataValidator:
    """Handles data validation between source and target PostgreSQL databases"""
    
    def __init__(self):
        self.source_table_prefix = ""  # Source tables: products, employees, orders
        self.target_table_prefix = "new_"  # Target tables: new_products, new_employees, new_orders
        
    def _get_postgresql_connection(self):
        """Get PostgreSQL connection using the same configuration as smoke tests"""
        # Set up smoke tester to get connection config
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
        else:
            username = os.getenv(effective_config.get('username_env_var'))
            password = os.getenv(effective_config.get('password_env_var'))
        
        # Create connector
        connector = PostgreSQLConnector(
            host=effective_config['host'],
            port=effective_config['port'],
            username=username,
            password=password,
            database=effective_config['database']
        )
        
        # Connect
        success, message = connector.connect()
        if not success:
            raise Exception(f"PostgreSQL connection failed: {message}")
            
        return connector
    
    def schema_validation_compare(self, source_table: str, target_table: str) -> ValidationResult:
        """Compare schema between source and target tables in PostgreSQL"""
        
        try:
            # Add prefixes to table names
            full_target_table = f"{self.target_table_prefix}{source_table}"
            
            # Connect to PostgreSQL
            connector = self._get_postgresql_connection()
            cursor = connector.connection.cursor()
            
            # Get source schema
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """, (source_table,))
            source_schema = cursor.fetchall()
            
            # Get target schema
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """, (full_target_table,))
            target_schema = cursor.fetchall()
            
            # Compare schemas
            source_columns = {col[0]: {'type': col[1], 'length': col[2], 'precision': col[3], 'scale': col[4], 'nullable': col[5]} for col in source_schema}
            target_columns = {col[0]: {'type': col[1], 'length': col[2], 'precision': col[3], 'scale': col[4], 'nullable': col[5]} for col in target_schema}
            
            differences = []
            
            # Check for missing columns in target
            for col_name, col_info in source_columns.items():
                if col_name not in target_columns:
                    differences.append(f"Missing column in target: {col_name} ({col_info['type']})")
                elif source_columns[col_name]['type'] != target_columns[col_name]['type']:
                    differences.append(f"Type mismatch for {col_name}: source={col_info['type']}, target={target_columns[col_name]['type']}")
                elif source_columns[col_name]['length'] != target_columns[col_name]['length']:
                    differences.append(f"Length mismatch for {col_name}: source={col_info['length']}, target={target_columns[col_name]['length']}")
            
            # Check for extra columns in target
            for col_name, col_info in target_columns.items():
                if col_name not in source_columns:
                    differences.append(f"Extra column in target: {col_name} ({col_info['type']})")
            
            connector.disconnect()
            
            if differences:
                return ValidationResult(
                    passed=False,
                    message=f"Schema differences found between {source_table} and {full_target_table}",
                    details={"differences": differences, "source_columns": len(source_columns), "target_columns": len(target_columns)}
                )
            else:
                return ValidationResult(
                    passed=True,
                    message=f"Schema validation passed for {source_table} vs {full_target_table}",
                    details={"source_columns": len(source_columns), "target_columns": len(target_columns)}
                )
                
        except Exception as e:
            return ValidationResult(
                passed=False,
                message=f"Schema validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def row_count_validation_compare(self, source_table: str, target_table: str) -> ValidationResult:
        """Compare row counts between source and target tables in PostgreSQL"""
        
        try:
            # Add prefixes to table names
            full_target_table = f"{self.target_table_prefix}{source_table}"
            
            # Connect to PostgreSQL
            connector = self._get_postgresql_connection()
            cursor = connector.connection.cursor()
            
            # Get row counts
            cursor.execute(f"SELECT COUNT(*) FROM {source_table}")
            source_count = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT COUNT(*) FROM {full_target_table}")
            target_count = cursor.fetchone()[0]
            
            connector.disconnect()
            
            if source_count == target_count:
                return ValidationResult(
                    passed=True,
                    message=f"Row count validation passed: {source_count} rows in both tables",
                    details={"source_count": source_count, "target_count": target_count}
                )
            else:
                return ValidationResult(
                    passed=False,
                    message=f"Row count mismatch: source={source_count}, target={target_count}",
                    details={"source_count": source_count, "target_count": target_count, "difference": abs(source_count - target_count)}
                )
                
        except Exception as e:
            return ValidationResult(
                passed=False,
                message=f"Row count validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def null_value_validation_compare(self, source_table: str, target_table: str) -> ValidationResult:
        """Compare NULL value patterns between source and target tables in PostgreSQL"""
        
        try:
            # Add prefixes to table names
            full_target_table = f"{self.target_table_prefix}{source_table}"
            
            # Connect to PostgreSQL
            connector = self._get_postgresql_connection()
            cursor = connector.connection.cursor()
            
            # Get common columns
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = %s
            """, (source_table,))
            source_columns = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = %s
            """, (full_target_table,))
            target_columns = [row[0] for row in cursor.fetchall()]
            
            common_columns = set(source_columns) & set(target_columns)
            
            null_differences = []
            
            for column in common_columns:
                # Count NULLs in source
                cursor.execute(f"SELECT COUNT(*) FROM {source_table} WHERE {column} IS NULL")
                source_nulls = cursor.fetchone()[0]
                
                # Count NULLs in target
                cursor.execute(f"SELECT COUNT(*) FROM {full_target_table} WHERE {column} IS NULL")
                target_nulls = cursor.fetchone()[0]
                
                if source_nulls != target_nulls:
                    null_differences.append({
                        "column": column,
                        "source_nulls": source_nulls,
                        "target_nulls": target_nulls,
                        "difference": abs(source_nulls - target_nulls)
                    })
            
            connector.disconnect()
            
            if null_differences:
                return ValidationResult(
                    passed=False,
                    message=f"NULL value differences found in {len(null_differences)} columns",
                    details={"differences": null_differences, "common_columns": len(common_columns)}
                )
            else:
                return ValidationResult(
                    passed=True,
                    message=f"NULL value validation passed for {len(common_columns)} common columns",
                    details={"common_columns": len(common_columns)}
                )
                
        except Exception as e:
            return ValidationResult(
                passed=False,
                message=f"NULL value validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def data_quality_validation_compare(self, source_table: str, target_table: str) -> ValidationResult:
        """Check data quality issues in target compared to source in PostgreSQL"""
        
        try:
            # Add prefixes to table names
            full_target_table = f"{self.target_table_prefix}{source_table}"
            
            # Connect to PostgreSQL
            connector = self._get_postgresql_connection()
            cursor = connector.connection.cursor()
            
            issues = []
            
            # Check for duplicates in target (assuming source has no duplicates)
            # Get primary key column (usually first column)
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position LIMIT 1
            """, (full_target_table,))
            
            pk_result = cursor.fetchone()
            if pk_result:
                id_column = pk_result[0]
                cursor.execute(f"""
                    SELECT {id_column}, COUNT(*) as cnt 
                    FROM {full_target_table} 
                    GROUP BY {id_column} 
                    HAVING COUNT(*) > 1
                """)
                duplicates = cursor.fetchall()
                
                if duplicates:
                    issues.append(f"Found {len(duplicates)} duplicate {id_column} values in target")
            
            # Check for orphaned records (basic foreign key validation)
            if target_table == "orders":
                # Use the actual target_table with prefix for orphaned records check
                full_orders_table = f"{self.target_table_prefix}{target_table}"
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {full_orders_table} o 
                    LEFT JOIN new_employees e ON o.employee_id = e.employee_id 
                    WHERE o.employee_id IS NOT NULL AND e.employee_id IS NULL
                """)
                orphaned_result = cursor.fetchone()
                if orphaned_result and orphaned_result[0] > 0:
                    orphaned = orphaned_result[0]
                    issues.append(f"Found {orphaned} orphaned orders with invalid employee_id")
            
            connector.disconnect()
            
            if issues:
                return ValidationResult(
                    passed=False,
                    message=f"Data quality issues found: {', '.join(issues)}",
                    details={"issues": issues}
                )
            else:
                return ValidationResult(
                    passed=True,
                    message="Data quality validation passed",
                    details={"checks_performed": ["duplicates", "foreign_keys"]}
                )
                
        except Exception as e:
            return ValidationResult(
                passed=False,
                message=f"Data quality validation failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def column_compare_validation(self, source_table: str, target_table: str, column_name: str) -> ValidationResult:
        """Compare specific column values between source and target in PostgreSQL"""
        
        try:
            # Add prefixes to table names
            full_target_table = f"{self.target_table_prefix}{source_table}"
            
            # Connect to PostgreSQL
            connector = self._get_postgresql_connection()
            cursor = connector.connection.cursor()
            
            # Get primary key column (usually first column)
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position LIMIT 1
            """, (source_table,))
            
            pk_result = cursor.fetchone()
            if not pk_result:
                raise Exception(f"Could not determine primary key for {source_table}")
            
            pk_column = pk_result[0]
            
            # Get source data
            cursor.execute(f"SELECT {pk_column}, {column_name} FROM {source_table} ORDER BY {pk_column}")
            source_data = dict(cursor.fetchall())
            
            # Get target data
            cursor.execute(f"SELECT {pk_column}, {column_name} FROM {full_target_table} ORDER BY {pk_column}")
            target_data = dict(cursor.fetchall())
            
            # Compare values
            differences = []
            common_keys = set(source_data.keys()) & set(target_data.keys())
            
            for key in common_keys:
                if source_data[key] != target_data[key]:
                    differences.append({
                        "id": key,
                        "source_value": source_data[key],
                        "target_value": target_data[key]
                    })
            
            # Check for missing keys
            missing_in_target = set(source_data.keys()) - set(target_data.keys())
            missing_in_source = set(target_data.keys()) - set(source_data.keys())
            
            connector.disconnect()
            
            if differences or missing_in_target or missing_in_source:
                return ValidationResult(
                    passed=False,
                    message=f"Column comparison failed for {column_name}: {len(differences)} value differences, {len(missing_in_target)} missing in target, {len(missing_in_source)} missing in source",
                    details={
                        "differences": differences[:10],  # Limit to first 10
                        "missing_in_target": list(missing_in_target),
                        "missing_in_source": list(missing_in_source),
                        "total_differences": len(differences)
                    }
                )
            else:
                return ValidationResult(
                    passed=True,
                    message=f"Column comparison passed for {column_name} ({len(common_keys)} records matched)",
                    details={"records_compared": len(common_keys)}
                )
                
        except Exception as e:
            return ValidationResult(
                passed=False,
                message=f"Column comparison failed: {str(e)}",
                details={"error": str(e)}
            )