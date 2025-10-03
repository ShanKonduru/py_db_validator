"""
Database connection data class
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class DatabaseConnection:
    """Data class representing a database connection configuration"""
    db_type: str
    host: str
    port: int
    database: str
    schema: Optional[str] = None
    username_env: Optional[str] = None
    password_env: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "db_type": self.db_type,
            "host": self.host,
            "port": self.port,
            "database": self.database
        }
        if self.schema:
            result["schema"] = self.schema
        if self.username_env:
            result["username_env"] = self.username_env
        if self.password_env:
            result["password_env"] = self.password_env
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseConnection':
        """Create from dictionary"""
        return cls(
            db_type=data["db_type"],
            host=data["host"],
            port=data["port"],
            database=data["database"],
            schema=data.get("schema"),
            username_env=data.get("username_env"),
            password_env=data.get("password_env")
        )