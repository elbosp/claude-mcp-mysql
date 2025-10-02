# MySQL MCP Server Setup Guide

## Configuration Created

I've created an MCP (Model Context Protocol) server configuration for MySQL with DML-only permissions at:
`~/.config/claude/claude_desktop_config.json`

## Next Steps

### 1. Update MySQL Credentials

Edit the configuration file to add your actual MySQL credentials:

```bash
nano ~/.config/claude/claude_desktop_config.json
```

Replace these placeholders with your actual values:
- `your_mysql_username` → Your MySQL username
- `your_mysql_password` → Your MySQL password
- `your_database_name` → The database you want to access

### 2. Create a Restricted MySQL User (Recommended)

For security, create a dedicated MySQL user with only DML permissions:

```sql
-- Connect to MySQL as root or admin user
mysql -u root -p

-- Create a new user for MCP access
CREATE USER 'mcp_user'@'localhost' IDENTIFIED BY 'strong_password_here';

-- Grant only DML permissions on your database
GRANT SELECT, INSERT, UPDATE, DELETE ON your_database.* TO 'mcp_user'@'localhost';

-- Apply the changes
FLUSH PRIVILEGES;
```

### 3. Verify MySQL is Running

Check that MySQL is running on your system:

```bash
# Check MySQL status
mysql.server status

# If not running, start it:
mysql.server start
```

### 4. Test the Connection

You can test your MySQL connection directly:

```bash
mysql -h 127.0.0.1 -P 3306 -u your_username -p your_database
```

### 5. Restart Claude Desktop

After updating the configuration:
1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. The MCP server should now be available

## Configuration Details

The configuration enables:
- **DML Operations**: INSERT, UPDATE, DELETE queries
- **Read Operations**: SELECT queries
- **Blocked**: All DDL operations (CREATE, ALTER, DROP, etc.)

### Performance Settings:
- Connection pool: 10 connections
- Query timeout: 30 seconds
- Cache TTL: 60 seconds
- Rate limit: 100 queries per minute

## Troubleshooting

If the MCP server doesn't appear:
1. Run `/doctor` in Claude to check for issues
2. Verify npm is installed: `which npm`
3. Check the configuration file syntax
4. Ensure MySQL credentials are correct
5. Check Claude Desktop logs for errors

## Security Best Practices

1. **Never use root MySQL credentials**
2. **Create a dedicated user with minimal permissions**
3. **Use strong passwords**
4. **Limit access to specific databases only**
5. **Consider using environment variables for sensitive data**

## Alternative: Using Environment Variables

For better security, you can store credentials in environment variables:

1. Create a `.env` file in a secure location
2. Set variables:
   ```
   MYSQL_USER=mcp_user
   MYSQL_PASSWORD=your_secure_password
   MYSQL_DATABASE=your_database
   ```
3. Source the file before starting Claude Desktop

## Available MCP Commands

Once configured, you'll be able to:
- Query data: `SELECT * FROM table_name`
- Insert records: `INSERT INTO table_name ...`
- Update records: `UPDATE table_name SET ...`
- Delete records: `DELETE FROM table_name ...`

All DDL operations will be blocked for safety.