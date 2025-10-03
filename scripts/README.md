# Scripts Directory

This directory contains automation scripts for setting up and running the Database Validation Framework on different operating systems.

## 📁 **Script Organization**

### Windows (Batch Files - `.bat`)
- `000_init.bat` - Initialize git repository and configure user settings
- `001_env.bat` - Create Python virtual environment  
- `002_activate.bat` - Activate virtual environment
- `003_setup.bat` - Install dependencies and upgrade pip
- `004_run.bat` - Run the database validation framework
- `005_run_test.bat` - Run tests and generate HTML report
- `005_run_code_cov.bat` - Run tests with code coverage
- `008_deactivate.bat` - Deactivate virtual environment

### Linux/Mac (Shell Scripts - `.sh`)
- `000_init.sh` - Initialize git repository and configure user settings
- `001_env.sh` - Create Python virtual environment
- `002_activate.sh` - Activate virtual environment (use with `source`)
- `003_setup.sh` - Install dependencies and upgrade pip  
- `004_run.sh` - Run the database validation framework
- `005_run_test.sh` - Run tests and generate HTML report
- `005_run_code_cov.sh` - Run tests with code coverage
- `008_deactivate.sh` - Deactivate virtual environment

## 🚀 **Quick Start**

### Windows
```cmd
# 1. Initialize git (optional)
scripts\000_init.bat

# 2. Create virtual environment
scripts\001_env.bat

# 3. Activate virtual environment
scripts\002_activate.bat

# 4. Install dependencies
scripts\003_setup.bat

# 5. Run tests
scripts\005_run_test.bat

# 6. Run with coverage
scripts\005_run_code_cov.bat

# 7. Run application (when ready)
scripts\004_run.bat

# 8. Deactivate when done
scripts\008_deactivate.bat
```

### Linux/Mac
```bash
# 1. Make scripts executable
chmod +x scripts/*.sh

# 2. Initialize git (optional)
./scripts/000_init.sh

# 3. Create virtual environment
./scripts/001_env.sh

# 4. Activate virtual environment (use source!)
source scripts/002_activate.sh

# 5. Install dependencies
./scripts/003_setup.sh

# 6. Run tests
./scripts/005_run_test.sh

# 7. Run with coverage
./scripts/005_run_code_cov.sh

# 8. Run application (when ready)
./scripts/004_run.sh

# 9. Deactivate when done
./scripts/008_deactivate.sh
```

## ⚠️ **Important Notes**

### Virtual Environment Activation
- **Windows**: Simply run `scripts\002_activate.bat`
- **Linux/Mac**: Must use `source scripts/002_activate.sh` (not `./scripts/002_activate.sh`)

### Python Commands
- **Windows**: Uses `python` command
- **Linux/Mac**: Uses `python3` command (adjust if needed)

### File Paths
- **Windows**: Uses backslashes (`\`) for paths
- **Linux/Mac**: Uses forward slashes (`/`) for paths

### Prerequisites
- **Windows**: Python 3.7+ installed and in PATH
- **Linux/Mac**: Python 3.7+ installed (`python3` command available)
- Git installed (for initialization script)

## 🔧 **Customization**

### Git Configuration
Edit the git user name and email in:
- `000_init.bat` (Windows)
- `000_init.sh` (Linux/Mac)

### Python Version
If you need to use a different Python command:
- **Windows**: Edit `.bat` files to change `python` command
- **Linux/Mac**: Edit `.sh` files to change `python3` command

## 📊 **Script Outputs**

- **Tests**: HTML reports generated in `test_reports/`
- **Coverage**: HTML reports generated in `htmlcov/`
- **Application**: Output in `reports/` directory
- **Logs**: Check terminal output for execution details

## 🐛 **Troubleshooting**

### Permission Issues (Linux/Mac)
```bash
chmod +x scripts/*.sh
```

### Virtual Environment Not Found
Make sure you run the scripts in the correct order:
1. `001_env` (create environment)
2. `002_activate` (activate environment)
3. `003_setup` (install dependencies)

### Path Issues
All scripts should be run from the project root directory, not from within the `scripts/` folder.