"""
Streamlit Database Configuration Editor
A user-friendly interface for editing database connection configurations
"""
import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, Any, List
import copy

# Page configuration
st.set_page_config(
    page_title="Database Configuration Editor",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

class DatabaseConfigEditor:
    """Database configuration editor class"""
    
    def __init__(self):
        self.config_data = {}
        self.config_file_path = ""
        self.supported_db_types = ["oracle", "postgresql", "sqlserver"]
        
    def load_config_file(self, file_path: str) -> bool:
        """Load configuration from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            self.config_file_path = file_path
            return True
        except Exception as e:
            st.error(f"Error loading configuration file: {str(e)}")
            return False
    
    def save_config_file(self) -> bool:
        """Save configuration to file"""
        try:
            # Create backup
            backup_path = f"{self.config_file_path}.backup"
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
            
            # Save updated config
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving configuration file: {str(e)}")
            return False
    
    def get_environments(self) -> List[str]:
        """Get list of environments"""
        return list(self.config_data.get("environments", {}).keys())
    
    def get_applications(self, environment: str) -> List[str]:
        """Get list of applications for an environment"""
        env_data = self.config_data.get("environments", {}).get(environment, {})
        return list(env_data.get("applications", {}).keys())
    
    def add_environment(self, env_name: str, env_display_name: str, env_description: str) -> bool:
        """Add new environment"""
        try:
            if "environments" not in self.config_data:
                self.config_data["environments"] = {}
            
            if env_name in self.config_data["environments"]:
                st.error(f"Environment '{env_name}' already exists!")
                return False
            
            self.config_data["environments"][env_name] = {
                "name": env_display_name,
                "description": env_description,
                "applications": {}
            }
            return True
        except Exception as e:
            st.error(f"Error adding environment: {str(e)}")
            return False
    
    def add_application(self, environment: str, app_name: str, app_config: Dict[str, Any]) -> bool:
        """Add new application to environment"""
        try:
            if environment not in self.config_data.get("environments", {}):
                st.error(f"Environment '{environment}' not found!")
                return False
            
            if app_name in self.config_data["environments"][environment].get("applications", {}):
                st.error(f"Application '{app_name}' already exists in environment '{environment}'!")
                return False
            
            self.config_data["environments"][environment]["applications"][app_name] = app_config
            return True
        except Exception as e:
            st.error(f"Error adding application: {str(e)}")
            return False
    
    def update_application(self, environment: str, app_name: str, app_config: Dict[str, Any]) -> bool:
        """Update existing application configuration"""
        try:
            if environment not in self.config_data.get("environments", {}):
                st.error(f"Environment '{environment}' not found!")
                return False
            
            if app_name not in self.config_data["environments"][environment].get("applications", {}):
                st.error(f"Application '{app_name}' not found in environment '{environment}'!")
                return False
            
            self.config_data["environments"][environment]["applications"][app_name] = app_config
            return True
        except Exception as e:
            st.error(f"Error updating application: {str(e)}")
            return False

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    if 'config_editor' not in st.session_state:
        st.session_state.config_editor = DatabaseConfigEditor()
    if 'config_loaded' not in st.session_state:
        st.session_state.config_loaded = False
    if 'unsaved_changes' not in st.session_state:
        st.session_state.unsaved_changes = False
    
    editor = st.session_state.config_editor
    
    # Title
    st.markdown('<h1 class="main-header">🗄️ Database Configuration Editor</h1>', unsafe_allow_html=True)
    
    # Sidebar for file operations
    with st.sidebar:
        st.markdown("### 📁 File Operations")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload Configuration File",
            type=['json'],
            help="Upload a database configuration JSON file"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if editor.load_config_file(temp_path):
                st.session_state.config_loaded = True
                st.success("✅ Configuration file loaded successfully!")
                os.remove(temp_path)  # Clean up temp file
            else:
                os.remove(temp_path)  # Clean up temp file
        
        # Or load from default path
        st.markdown("---")
        default_config_path = "config/database_connections.json"
        if st.button("📂 Load Default Config"):
            if os.path.exists(default_config_path):
                if editor.load_config_file(default_config_path):
                    st.session_state.config_loaded = True
                    st.success("✅ Default configuration loaded!")
            else:
                st.error("❌ Default configuration file not found!")
        
        # Save button
        if st.session_state.config_loaded:
            st.markdown("---")
            if st.button("💾 Save Configuration", type="primary"):
                if editor.save_config_file():
                    st.success("✅ Configuration saved successfully!")
                    st.session_state.unsaved_changes = False
                    st.rerun()
        
        # Show file info
        if st.session_state.config_loaded:
            st.markdown("---")
            st.markdown("### 📋 File Information")
            st.info(f"📄 **File:** {editor.config_file_path}")
            if st.session_state.unsaved_changes:
                st.warning("⚠️ Unsaved changes")
    
    # Main content
    if not st.session_state.config_loaded:
        st.markdown("""
        <div style="text-align: center; margin-top: 3rem;">
            <h3>👋 Welcome to Database Configuration Editor</h3>
            <p>Please upload a configuration file or load the default configuration to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Configuration overview
    st.markdown('<h2 class="section-header">📊 Configuration Overview</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        env_count = len(editor.get_environments())
        st.metric("🌍 Environments", env_count)
    
    with col2:
        total_apps = sum(len(editor.get_applications(env)) for env in editor.get_environments())
        st.metric("📱 Total Applications", total_apps)
    
    with col3:
        db_types = set()
        for env in editor.get_environments():
            for app in editor.get_applications(env):
                app_config = editor.config_data["environments"][env]["applications"][app]
                db_types.add(app_config.get("db_type", "unknown"))
        st.metric("🗃️ Database Types", len(db_types))
    
    # Tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 View/Edit", "🌍 Add Environment", "📱 Add Application", "📋 Metadata"])
    
    with tab1:
        view_edit_tab(editor)
    
    with tab2:
        add_environment_tab(editor)
    
    with tab3:
        add_application_tab(editor)
    
    with tab4:
        metadata_tab(editor)

def view_edit_tab(editor):
    """View and edit existing configurations"""
    st.markdown("### 🔍 View and Edit Configurations")
    
    environments = editor.get_environments()
    if not environments:
        st.warning("No environments found in the configuration.")
        return
    
    # Environment selection
    selected_env = st.selectbox(
        "Select Environment",
        environments,
        help="Choose an environment to view and edit"
    )
    
    if selected_env:
        env_data = editor.config_data["environments"][selected_env]
        
        # Environment details
        st.markdown(f"#### Environment: **{selected_env}**")
        
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Environment Name", value=env_data.get("name", selected_env))
        with col2:
            new_description = st.text_area("Environment Description", value=env_data.get("description", ""))
        
        # Update environment details
        if st.button("Update Environment Details"):
            editor.config_data["environments"][selected_env]["name"] = new_name
            editor.config_data["environments"][selected_env]["description"] = new_description
            st.session_state.unsaved_changes = True
            st.success("Environment details updated!")
            st.rerun()
        
        # Applications in environment
        applications = editor.get_applications(selected_env)
        if applications:
            st.markdown("---")
            st.markdown("#### Applications")
            
            selected_app = st.selectbox(
                "Select Application",
                applications,
                help="Choose an application to edit"
            )
            
            if selected_app:
                app_config = editor.config_data["environments"][selected_env]["applications"][selected_app]
                
                st.markdown(f"##### Application: **{selected_app}**")
                
                # Create form for editing application
                with st.form(f"edit_app_{selected_env}_{selected_app}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        db_type = st.selectbox("Database Type", editor.supported_db_types, 
                                             index=editor.supported_db_types.index(app_config.get("db_type", "oracle")))
                        host = st.text_input("Host", value=app_config.get("host", ""))
                        port = st.number_input("Port", value=app_config.get("port", 1521), min_value=1, max_value=65535)
                        
                        if db_type == "oracle":
                            service_name = st.text_input("Service Name", value=app_config.get("service_name", ""))
                        elif db_type in ["postgresql", "sqlserver"]:
                            database = st.text_input("Database", value=app_config.get("database", ""))
                        
                        schema = st.text_input("Schema", value=app_config.get("schema", ""))
                    
                    with col2:
                        username_env_var = st.text_input("Username Environment Variable", 
                                                       value=app_config.get("username_env_var", ""))
                        password_env_var = st.text_input("Password Environment Variable", 
                                                       value=app_config.get("password_env_var", ""))
                        connection_timeout = st.number_input("Connection Timeout (seconds)", 
                                                           value=app_config.get("connection_timeout", 30), min_value=1)
                        query_timeout = st.number_input("Query Timeout (seconds)", 
                                                      value=app_config.get("query_timeout", 300), min_value=1)
                        max_connections = st.number_input("Max Connections", 
                                                        value=app_config.get("max_connections", 10), min_value=1)
                    
                    # Submit button
                    if st.form_submit_button("💾 Update Application", type="primary"):
                        new_config = {
                            "db_type": db_type,
                            "host": host,
                            "port": port,
                            "schema": schema,
                            "username_env_var": username_env_var,
                            "password_env_var": password_env_var,
                            "connection_timeout": connection_timeout,
                            "query_timeout": query_timeout,
                            "max_connections": max_connections
                        }
                        
                        # Add database-specific fields
                        if db_type == "oracle":
                            new_config["service_name"] = service_name
                        elif db_type in ["postgresql", "sqlserver"]:
                            new_config["database"] = database
                        
                        if editor.update_application(selected_env, selected_app, new_config):
                            st.session_state.unsaved_changes = True
                            st.success(f"Application '{selected_app}' updated successfully!")
                            st.rerun()
        else:
            st.info("No applications found in this environment.")

def add_environment_tab(editor):
    """Add new environment"""
    st.markdown("### 🌍 Add New Environment")
    
    with st.form("add_environment"):
        col1, col2 = st.columns(2)
        
        with col1:
            env_name = st.text_input("Environment Code", placeholder="e.g., PROD, STAGE")
            env_display_name = st.text_input("Environment Name", placeholder="e.g., Production")
        
        with col2:
            env_description = st.text_area("Description", placeholder="Environment description...")
        
        if st.form_submit_button("➕ Add Environment", type="primary"):
            if env_name and env_display_name:
                if editor.add_environment(env_name.upper(), env_display_name, env_description):
                    st.session_state.unsaved_changes = True
                    st.success(f"Environment '{env_name}' added successfully!")
                    st.rerun()
            else:
                st.error("Environment code and name are required!")

def add_application_tab(editor):
    """Add new application"""
    st.markdown("### 📱 Add New Application")
    
    environments = editor.get_environments()
    if not environments:
        st.warning("No environments available. Please add an environment first.")
        return
    
    with st.form("add_application"):
        # Basic info
        col1, col2 = st.columns(2)
        
        with col1:
            target_env = st.selectbox("Target Environment", environments)
            app_name = st.text_input("Application Code", placeholder="e.g., RED, TPS")
            db_type = st.selectbox("Database Type", editor.supported_db_types)
        
        with col2:
            host = st.text_input("Host", placeholder="e.g., db.company.com")
            port = st.number_input("Port", value=1521 if db_type == "oracle" else 5432, min_value=1, max_value=65535)
            schema = st.text_input("Schema", placeholder="Schema name")
        
        # Database-specific fields
        if db_type == "oracle":
            service_name = st.text_input("Service Name", placeholder="Oracle service name")
        elif db_type in ["postgresql", "sqlserver"]:
            database = st.text_input("Database", placeholder="Database name")
        
        # Environment variables
        col3, col4 = st.columns(2)
        with col3:
            username_env_var = st.text_input("Username Environment Variable", 
                                           placeholder=f"{target_env}_{app_name}_USERNAME")
        with col4:
            password_env_var = st.text_input("Password Environment Variable", 
                                           placeholder=f"{target_env}_{app_name}_PASSWORD")
        
        # Connection settings
        col5, col6, col7 = st.columns(3)
        with col5:
            connection_timeout = st.number_input("Connection Timeout (seconds)", value=30, min_value=1)
        with col6:
            query_timeout = st.number_input("Query Timeout (seconds)", value=300, min_value=1)
        with col7:
            max_connections = st.number_input("Max Connections", value=10, min_value=1)
        
        if st.form_submit_button("➕ Add Application", type="primary"):
            if app_name and host:
                new_config = {
                    "db_type": db_type,
                    "host": host,
                    "port": port,
                    "schema": schema,
                    "username_env_var": username_env_var or f"{target_env}_{app_name}_USERNAME",
                    "password_env_var": password_env_var or f"{target_env}_{app_name}_PASSWORD",
                    "connection_timeout": connection_timeout,
                    "query_timeout": query_timeout,
                    "max_connections": max_connections
                }
                
                # Add database-specific fields
                if db_type == "oracle":
                    new_config["service_name"] = service_name
                elif db_type in ["postgresql", "sqlserver"]:
                    new_config["database"] = database
                
                if editor.add_application(target_env, app_name.upper(), new_config):
                    st.session_state.unsaved_changes = True
                    st.success(f"Application '{app_name}' added to environment '{target_env}'!")
                    st.rerun()
            else:
                st.error("Application code and host are required!")

def metadata_tab(editor):
    """View and edit metadata"""
    st.markdown("### 📋 Configuration Metadata")
    
    metadata = editor.config_data.get("metadata", {})
    
    with st.form("edit_metadata"):
        col1, col2 = st.columns(2)
        
        with col1:
            config_version = st.text_input("Config Version", value=metadata.get("config_version", "1.0"))
            created_date = st.date_input("Created Date", 
                                       value=pd.to_datetime(metadata.get("created_date", "2025-01-01")).date())
        
        with col2:
            description = st.text_area("Description", value=metadata.get("description", ""))
        
        # Supported environments
        st.markdown("#### Supported Environments")
        supported_envs = st.text_area("Supported Environments (one per line)", 
                                     value="\n".join(metadata.get("supported_environments", [])))
        
        # Supported applications
        st.markdown("#### Supported Applications")
        supported_apps = metadata.get("supported_applications", {})
        app_descriptions = "\n".join([f"{app}: {desc}" for app, desc in supported_apps.items()])
        new_app_descriptions = st.text_area("Supported Applications (format: APP: Description)", 
                                           value=app_descriptions)
        
        if st.form_submit_button("💾 Update Metadata", type="primary"):
            # Parse supported environments
            env_list = [env.strip() for env in supported_envs.split('\n') if env.strip()]
            
            # Parse supported applications
            app_dict = {}
            for line in new_app_descriptions.split('\n'):
                if ':' in line:
                    app, desc = line.split(':', 1)
                    app_dict[app.strip()] = desc.strip()
            
            # Update metadata
            editor.config_data["metadata"] = {
                "config_version": config_version,
                "created_date": created_date.strftime("%Y-%m-%d"),
                "description": description,
                "supported_environments": env_list,
                "supported_applications": app_dict
            }
            
            st.session_state.unsaved_changes = True
            st.success("Metadata updated successfully!")
            st.rerun()
    
    # Display current metadata
    st.markdown("---")
    st.markdown("#### Current Metadata")
    st.json(metadata)

if __name__ == "__main__":
    # Required import for date handling
    import pandas as pd
    main()