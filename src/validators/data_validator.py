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
    
    def _format_column_type(self, col_info: dict) -> str:
        """Format column type information for display"""
        data_type = col_info['type']
        length = col_info['length']
        precision = col_info['precision']
        scale = col_info['scale']
        nullable = col_info['nullable']
        
        # Format the type string
        if data_type in ['character varying', 'varchar']:
            type_str = f"VARCHAR({length})" if length else "VARCHAR"
        elif data_type == 'character':
            type_str = f"CHAR({length})" if length else "CHAR"
        elif data_type == 'text':
            type_str = "TEXT"
        elif data_type == 'numeric':
            if precision and scale:
                type_str = f"NUMERIC({precision},{scale})"
            elif precision:
                type_str = f"NUMERIC({precision})"
            else:
                type_str = "NUMERIC"
        elif data_type == 'integer':
            type_str = "INTEGER"
        elif data_type == 'bigint':
            type_str = "BIGINT"
        elif data_type == 'smallint':
            type_str = "SMALLINT"
        elif data_type == 'boolean':
            type_str = "BOOLEAN"
        elif data_type == 'date':
            type_str = "DATE"
        elif data_type == 'timestamp without time zone':
            type_str = "TIMESTAMP"
        elif data_type == 'timestamp with time zone':
            type_str = "TIMESTAMPTZ"
        else:
            type_str = data_type.upper()
        
        # Add nullable info
        if nullable == 'NO':
            type_str += " NOT NULL"
        
        return type_str
    
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
            detailed_report = []
            
            # Check for missing columns in target
            for col_name, col_info in source_columns.items():
                if col_name not in target_columns:
                    differences.append(f"Missing column in target: {col_name} ({col_info['type']})")
                    detailed_report.append({
                        'column': col_name,
                        'issue': 'MISSING_IN_TARGET',
                        'source_type': self._format_column_type(col_info),
                        'target_type': 'N/A',
                        'description': f"Column '{col_name}' exists in source but missing in target table"
                    })
                else:
                    # Compare column properties
                    src_type_str = self._format_column_type(col_info)
                    tgt_type_str = self._format_column_type(target_columns[col_name])
                    
                    if col_info != target_columns[col_name]:
                        differences.append(f"Column difference: {col_name}")
                        detailed_report.append({
                            'column': col_name,
                            'issue': 'SCHEMA_MISMATCH',
                            'source_type': src_type_str,
                            'target_type': tgt_type_str,
                            'description': f"Column '{col_name}' has different properties between source and target"
                        })
            
            # Check for extra columns in target
            for col_name, col_info in target_columns.items():
                if col_name not in source_columns:
                    differences.append(f"Extra column in target: {col_name} ({col_info['type']})")
                    detailed_report.append({
                        'column': col_name,
                        'issue': 'EXTRA_IN_TARGET',
                        'source_type': 'N/A',
                        'target_type': self._format_column_type(col_info),
                        'description': f"Column '{col_name}' exists in target but missing in source table"
                    })
            
            connector.disconnect()
            
            if differences:
                return ValidationResult(
                    passed=False,
                    message=f"Schema differences found between {source_table} and {full_target_table}",
                    details={
                        "differences": differences, 
                        "source_columns": len(source_columns), 
                        "target_columns": len(target_columns),
                        "detailed_report": detailed_report,
                        "source_table": source_table,
                        "target_table": full_target_table
                    }
                )
            else:
                return ValidationResult(
                    passed=True,
                    message=f"Schema validation passed for {source_table} vs {full_target_table}",
                    details={
                        "source_columns": len(source_columns), 
                        "target_columns": len(target_columns),
                        "source_table": source_table,
                        "target_table": full_target_table
                    }
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
            
            # Get common columns with their constraints
            cursor.execute("""
                SELECT c.column_name, c.is_nullable, c.data_type 
                FROM information_schema.columns c
                WHERE c.table_schema = 'public' AND c.table_name = %s
                ORDER BY c.ordinal_position
            """, (source_table,))
            source_columns = {row[0]: {"nullable": row[1], "type": row[2]} for row in cursor.fetchall()}
            
            cursor.execute("""
                SELECT c.column_name, c.is_nullable, c.data_type 
                FROM information_schema.columns c
                WHERE c.table_schema = 'public' AND c.table_name = %s
                ORDER BY c.ordinal_position
            """, (full_target_table,))
            target_columns = {row[0]: {"nullable": row[1], "type": row[2]} for row in cursor.fetchall()}
            
            common_columns = set(source_columns.keys()) & set(target_columns.keys())
            
            # Get total row counts
            cursor.execute(f"SELECT COUNT(*) FROM {source_table}")
            source_total = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT COUNT(*) FROM {full_target_table}")
            target_total = cursor.fetchone()[0]
            
            null_differences = []
            
            for column in sorted(common_columns):
                # Count NULLs in source
                cursor.execute(f"SELECT COUNT(*) FROM {source_table} WHERE {column} IS NULL")
                source_nulls = cursor.fetchone()[0]
                
                # Count NULLs in target
                cursor.execute(f"SELECT COUNT(*) FROM {full_target_table} WHERE {column} IS NULL")
                target_nulls = cursor.fetchone()[0]
                
                # Calculate percentages
                source_null_pct = (source_nulls / source_total * 100) if source_total > 0 else 0
                target_null_pct = (target_nulls / target_total * 100) if target_total > 0 else 0
                
                # Check for differences or constraint violations
                has_difference = source_nulls != target_nulls
                constraint_violation = False
                
                # Check if NOT NULL column has NULLs
                source_nullable = source_columns[column]["nullable"] == "YES"
                target_nullable = target_columns[column]["nullable"] == "YES"
                
                if not source_nullable and source_nulls > 0:
                    constraint_violation = True
                if not target_nullable and target_nulls > 0:
                    constraint_violation = True
                
                if has_difference or constraint_violation:
                    issue_type = "CONSTRAINT_VIOLATION" if constraint_violation else "NULL_COUNT_MISMATCH"
                    
                    null_differences.append({
                        "column": column,
                        "issue_type": issue_type,
                        "data_type": source_columns[column]["type"],
                        "source_nullable": source_nullable,
                        "target_nullable": target_nullable,
                        "source_nulls": source_nulls,
                        "target_nulls": target_nulls,
                        "source_null_percentage": round(source_null_pct, 2),
                        "target_null_percentage": round(target_null_pct, 2),
                        "difference": abs(source_nulls - target_nulls),
                        "source_total": source_total,
                        "target_total": target_total
                    })
            
            connector.disconnect()
            
            if null_differences:
                return ValidationResult(
                    passed=False,
                    message=f"NULL value differences found in {len(null_differences)} columns",
                    details={
                        "null_differences": null_differences, 
                        "common_columns": len(common_columns),
                        "source_table": source_table,
                        "target_table": full_target_table,
                        "source_total_rows": source_total,
                        "target_total_rows": target_total
                    }
                )
            else:
                return ValidationResult(
                    passed=True,
                    message=f"NULL value validation passed for {len(common_columns)} common columns",
                    details={
                        "common_columns": len(common_columns),
                        "source_table": source_table,
                        "target_table": full_target_table,
                        "source_total_rows": source_total,
                        "target_total_rows": target_total
                    }
                )
                
        except Exception as e:
            return ValidationResult(
                passed=False,
                message=f"NULL value validation failed: {str(e)}",
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