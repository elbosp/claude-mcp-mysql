# Claude MCP MySQL Setup Guide

## Overview

Claude MCP MySQL is a Model Context Protocol (MCP) server that enables Claude to interact with MySQL databases. It provides safe DML (Data Manipulation Language) operations while blocking potentially dangerous DDL (Data Definition Language) and DELETE operations by default.

## Features

- Execute SELECT queries to retrieve data
- Execute INSERT queries to add new records
- Execute UPDATE queries to modify existing records
- Optional DELETE operation support (disabled by default)
- Optional DDL operation support (disabled by default)
- Database switching support
- Environment-based configuration

## Prerequisites

1. **Python 3.7+** installed on your system
2. **MySQL Server** installed and running
3. **Claude Desktop** application
4. Basic knowledge of MySQL and database operations

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/elbosp/claude-mcp-mysql.git
cd claude-mcp-mysql
```

### Step 2: Install Python Dependencies

```bash
pip install mysql-connector-python python-dotenv
```

Or create a virtual environment first (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install mysql-connector-python python-dotenv
```

### Step 3: Configure Database Connection

1. Copy the `.env.example` file (or create a new `.env` file):

```bash
cp .env.example .env  # Or create new file
```

2. Edit the `.env` file with your MySQL connection details:

```env
# MySQL Database Configuration
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password

# Optional: Specify a default database (leave empty for no default)
MYSQL_DATABASE=your_database

# Security Settings
ALLOW_DELETE=false  # Set to true to enable DELETE operations
ALLOW_DDL=false     # Set to true to enable CREATE, ALTER, DROP operations
```

### Step 4: Configure Claude Desktop

1. Open Claude Desktop settings
2. Navigate to the Developer section
3. Add the MCP server configuration to your settings:

**On macOS/Linux:**

```json
{
  "mcpServers": {
    "mysql-dml": {
      "command": "/usr/bin/python3",
      "args": ["/path/to/claude-mcp-mysql/mysql_mcp.py"]
    }
  }
}
```

**On Windows:**

```json
{
  "mcpServers": {
    "mysql-dml": {
      "command": "C:\\Python3X\\python.exe",
      "args": ["C:\\path\\to\\claude-mcp-mysql\\mysql_mcp.py"]
    }
  }
}
```

**Using Virtual Environment:**

```json
{
  "mcpServers": {
    "mysql-dml": {
      "command": "/path/to/claude-mcp-mysql/venv/bin/python",
      "args": ["/path/to/claude-mcp-mysql/mysql_mcp.py"]
    }
  }
}
```

4. Restart Claude Desktop to apply the changes

## Usage

Once configured, Claude can interact with your MySQL database using natural language. Here are some examples:

### Basic Queries

```sql
-- View all tables in the current database
SHOW TABLES;

-- Select data
SELECT * FROM users WHERE age > 18;

-- Insert data
INSERT INTO users (name, email, age) VALUES ('John Doe', 'john@example.com', 25);

-- Update data
UPDATE users SET email = 'newemail@example.com' WHERE id = 1;
```

### Working with Multiple Databases

You can switch between databases or specify a database for each query:

```python
# In Claude, you can ask:
"Show me all tables in the database 'myapp'"
"Select all users from the production database"
```

## Security Considerations

### Default Security Settings

- **DELETE operations**: Disabled by default
- **DDL operations** (CREATE, ALTER, DROP, TRUNCATE): Disabled by default
- Only DML operations (SELECT, INSERT, UPDATE) are allowed

### Enabling Additional Operations

To enable DELETE operations, set in `.env`:
```env
ALLOW_DELETE=true
```

To enable DDL operations, set in `.env`:
```env
ALLOW_DDL=true
```

**⚠️ Warning**: Enable these features only if you understand the risks. DDL operations can permanently alter your database structure.

## Troubleshooting

### Connection Issues

1. **Error: "Failed to connect to MySQL"**
   - Verify MySQL server is running
   - Check connection details in `.env`
   - Ensure user has proper permissions
   - Test connection using MySQL command line client

2. **Error: "Access denied for user"**
   - Verify username and password in `.env`
   - Ensure user has necessary privileges:
   ```sql
   GRANT SELECT, INSERT, UPDATE ON database_name.* TO 'username'@'host';
   ```

3. **Port Issues**
   - Default MySQL port is 3306
   - Check if port is blocked by firewall
   - Verify MySQL is listening on the correct port

### MCP Server Issues

1. **Server not appearing in Claude**
   - Ensure Claude Desktop is restarted after configuration
   - Check the path to Python and the script is correct
   - Verify Python dependencies are installed

2. **Permission errors**
   - Ensure the Python script has execute permissions:
   ```bash
   chmod +x mysql_mcp.py
   ```

### Query Issues

1. **"DDL operations are not allowed"**
   - This is by design for safety
   - Set `ALLOW_DDL=true` in `.env` if needed

2. **"DELETE operations are not allowed"**
   - This is by design for safety
   - Set `ALLOW_DELETE=true` in `.env` if needed

## Development

### Testing the Server Locally

You can test the MCP server directly:

```bash
# Run the server
python mysql_mcp.py

# Send test commands via stdin (JSON-RPC format)
{"jsonrpc":"2.0","id":1,"method":"initialize"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
```

### Extending Functionality

The server can be extended by:
1. Adding new tools in the `handle_list_tools` method
2. Implementing new query types
3. Adding additional security checks
4. Implementing query logging or auditing

## Best Practices

1. **Use Read-Only User**: For production, create a MySQL user with minimal required permissions
2. **Backup Data**: Always backup your database before allowing write operations
3. **Test First**: Test queries in a development environment first
4. **Monitor Activity**: Keep logs of database operations
5. **Limit Access**: Only enable DELETE and DDL operations when absolutely necessary

## Support

For issues, questions, or contributions:
- GitHub Repository: https://github.com/elbosp/claude-mcp-mysql
- Create an issue for bug reports or feature requests
- Submit pull requests for improvements

## License

[Add your license information here]

## Acknowledgments

Built for use with Claude Desktop and the Model Context Protocol (MCP).