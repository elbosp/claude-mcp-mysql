# Claude Code Agent Instructions for MySQL MCP Setup

## Automated Setup Instructions

When a user wants to set up the Claude MCP MySQL server, follow these steps automatically:

### 1. Environment Preparation

First, check if Python and required dependencies are installed:

```bash
# Check Python version
python3 --version

# Install required Python packages
pip install mysql-connector-python python-dotenv
```

If using a virtual environment is preferred:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install mysql-connector-python python-dotenv
```

### 2. Configure Database Connection

Create or update the `.env` file in the project root with the following template:

```env
# MySQL Database Configuration
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password

# Optional: Specify a default database (leave empty for no default)
MYSQL_DATABASE=

# Security Settings
ALLOW_DELETE=false
ALLOW_DDL=false
```

Ask the user for:
- MySQL host (default: 127.0.0.1)
- MySQL port (default: 3306)
- MySQL username
- MySQL password
- Default database name (optional)
- Whether to allow DELETE operations (default: false)
- Whether to allow DDL operations (default: false)

### 3. Configure Claude Desktop Settings

Locate and update the Claude Desktop configuration file:

**On macOS:**
- Config location: `~/Library/Application Support/Claude/claude_desktop_config.json`

**On Windows:**
- Config location: `%APPDATA%\Claude\claude_desktop_config.json`

**On Linux:**
- Config location: `~/.config/Claude/claude_desktop_config.json`

Add or update the MCP server configuration:

```json
{
  "mcpServers": {
    "mysql-dml": {
      "command": "<python_path>",
      "args": ["<full_path_to_mysql_mcp.py>"]
    }
  }
}
```

Where:
- `<python_path>` is the full path to Python executable (use `which python3` or `where python` to find it)
- `<full_path_to_mysql_mcp.py>` is the absolute path to the mysql_mcp.py file

### 4. Verification Steps

After configuration, verify the setup:

1. **Test Python script directly:**
```bash
python3 mysql_mcp.py
# Send test command:
{"jsonrpc":"2.0","id":1,"method":"initialize"}
# Press Ctrl+C to exit
```

2. **Test MySQL connection:**
```bash
mysql -h <host> -P <port> -u <username> -p
# Enter password when prompted
```

3. **Restart Claude Desktop** to load the new MCP configuration

4. **Verify in Claude Desktop:**
   - The MCP server should appear in the available tools
   - Test with a simple query like "SHOW DATABASES;"

## Automated Setup Script

Create and run this setup script to automate the entire process:

```python
#!/usr/bin/env python3
import os
import json
import subprocess
import sys
from pathlib import Path

def setup_mysql_mcp():
    """Automated setup for MySQL MCP"""

    print("🚀 Starting MySQL MCP Setup...")

    # Get current directory
    current_dir = Path.cwd()
    mysql_mcp_path = current_dir / "mysql_mcp.py"

    if not mysql_mcp_path.exists():
        print("❌ mysql_mcp.py not found in current directory!")
        return False

    # Step 1: Install dependencies
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install",
                       "mysql-connector-python", "python-dotenv"],
                       check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

    # Step 2: Configure .env file
    print("\n🔧 Configuring database connection...")
    env_file = current_dir / ".env"

    if env_file.exists():
        print("⚠️  .env file already exists. Please configure it manually.")
    else:
        # Get user input for configuration
        host = input("MySQL Host [127.0.0.1]: ").strip() or "127.0.0.1"
        port = input("MySQL Port [3306]: ").strip() or "3306"
        user = input("MySQL Username: ").strip()
        password = input("MySQL Password: ").strip()
        database = input("Default Database (optional): ").strip()
        allow_delete = input("Allow DELETE operations? [no]: ").strip().lower() in ['yes', 'y', 'true']
        allow_ddl = input("Allow DDL operations? [no]: ").strip().lower() in ['yes', 'y', 'true']

        # Write .env file
        env_content = f"""# MySQL Database Configuration
MYSQL_HOST={host}
MYSQL_PORT={port}
MYSQL_USER={user}
MYSQL_PASSWORD={password}

# Optional: Specify a default database (leave empty for no default)
MYSQL_DATABASE={database}

# Security Settings
ALLOW_DELETE={str(allow_delete).lower()}
ALLOW_DDL={str(allow_ddl).lower()}
"""
        env_file.write_text(env_content)
        print("✅ .env file created successfully")

    # Step 3: Configure Claude Desktop
    print("\n⚙️  Configuring Claude Desktop...")

    # Determine config path based on OS
    if sys.platform == "darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    elif sys.platform == "win32":  # Windows
        config_dir = Path(os.environ.get("APPDATA", "")) / "Claude"
    else:  # Linux
        config_dir = Path.home() / ".config" / "Claude"

    config_file = config_dir / "claude_desktop_config.json"

    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    # Load existing config or create new one
    config = {}
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
        except json.JSONDecodeError:
            print("⚠️  Existing config file is invalid, creating new one...")

    # Add MCP server configuration
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    config["mcpServers"]["mysql-dml"] = {
        "command": sys.executable,
        "args": [str(mysql_mcp_path.absolute())]
    }

    # Write updated config
    config_file.write_text(json.dumps(config, indent=2))
    print(f"✅ Claude Desktop config updated at: {config_file}")

    # Step 4: Test the setup
    print("\n🧪 Testing MySQL connection...")
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=host if 'host' in locals() else "127.0.0.1",
            port=int(port if 'port' in locals() else "3306"),
            user=user if 'user' in locals() else "",
            password=password if 'password' in locals() else ""
        )
        conn.close()
        print("✅ MySQL connection successful!")
    except Exception as e:
        print(f"⚠️  MySQL connection failed: {e}")
        print("   Please verify your MySQL server is running and credentials are correct.")

    print("\n✨ Setup complete!")
    print("\n📝 Next steps:")
    print("1. Restart Claude Desktop to load the new MCP configuration")
    print("2. In Claude, you can now use MySQL queries directly")
    print("3. Try asking Claude: 'Show me all databases' or 'SELECT * FROM your_table'")

    return True

if __name__ == "__main__":
    setup_mysql_mcp()
```

## Quick Commands for Claude Code Agent

When a user asks to set up MySQL MCP, execute these commands in sequence:

```bash
# 1. Install dependencies
pip install mysql-connector-python python-dotenv

# 2. Create .env file with user's credentials
cat > .env << 'EOF'
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=<ask_user>
MYSQL_PASSWORD=<ask_user>
MYSQL_DATABASE=
ALLOW_DELETE=false
ALLOW_DDL=false
EOF

# 3. Find Claude config location (macOS example)
CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# 4. Update Claude config (backup first)
cp "$CONFIG_PATH" "$CONFIG_PATH.backup"

# 5. Add MCP server to config
python3 -c "
import json
from pathlib import Path
config_path = Path('$CONFIG_PATH')
config = json.loads(config_path.read_text()) if config_path.exists() else {}
if 'mcpServers' not in config: config['mcpServers'] = {}
config['mcpServers']['mysql-dml'] = {
    'command': '$(which python3)',
    'args': ['$(pwd)/mysql_mcp.py']
}
config_path.write_text(json.dumps(config, indent=2))
print('Config updated successfully')
"

# 6. Test the connection
python3 -c "
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='password'
    )
    conn.close()
    print('✅ MySQL connection successful')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"

echo "✅ Setup complete! Please restart Claude Desktop."
```

## Troubleshooting Automation

If setup fails, automatically check:

1. **Python version**: Ensure Python 3.7+ is installed
2. **MySQL server**: Verify MySQL is running (`mysqladmin ping`)
3. **Permissions**: Check file permissions and Claude config access
4. **Dependencies**: Verify pip packages are installed correctly
5. **Config syntax**: Validate JSON syntax in Claude config file

## User Interaction Template

When helping a user set up MySQL MCP, use this interaction flow:

1. "I'll help you set up the MySQL MCP server for Claude. First, I need some information about your MySQL setup."
2. Gather necessary information (credentials, preferences)
3. Execute the automated setup steps
4. Verify the installation
5. Provide clear next steps and usage examples

## Error Recovery

If any step fails:
- Identify the specific failure point
- Provide clear error messages
- Offer alternative solutions
- Create rollback if configuration was partially modified
- Guide user through manual steps if automation fails

This prompt serves as a complete instruction set for Claude Code agents to automatically set up the MySQL MCP without requiring users to manually edit configuration files or follow complex setup procedures.