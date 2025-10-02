# MySQL MCP Server Usage Examples

## How to Use in Claude Code

Simply ask Claude to query your MySQL database in natural language. The MCP server will handle the SQL execution.

## Example Conversations

### 1. Basic Queries

**You can say:**
```
"Show me all databases in MySQL"
"List all tables in the beasiswa_core database"
"Query the users table and show me the first 10 records"
```

**Claude will execute:**
```sql
SHOW DATABASES;
SHOW TABLES FROM beasiswa_core;
SELECT * FROM users LIMIT 10;
```

### 2. Working with Specific Databases

**You can say:**
```
"Use the beasiswa_core database and show me the structure of the users table"
"What columns are in the products table in mydb?"
```

**Claude will execute:**
```sql
USE beasiswa_core;
DESCRIBE users;

DESCRIBE mydb.products;
```

### 3. Inserting Data

**You can say:**
```
"Insert a new user with name 'John Doe' and email 'john@example.com' into the users table"
"Add a new product to the products table with name 'Laptop' and price 999.99"
```

**Claude will execute:**
```sql
INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com');
INSERT INTO products (name, price) VALUES ('Laptop', 999.99);
```

### 4. Updating Data

**You can say:**
```
"Update the price of product with id 5 to 799.99"
"Change the status to 'active' for all users created today"
```

**Claude will execute:**
```sql
UPDATE products SET price = 799.99 WHERE id = 5;
UPDATE users SET status = 'active' WHERE DATE(created_at) = CURDATE();
```

### 5. Complex Queries

**You can say:**
```
"Show me the total number of users grouped by status"
"Find all orders from last month with their customer names"
```

**Claude will execute:**
```sql
SELECT status, COUNT(*) as total FROM users GROUP BY status;

SELECT o.*, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH);
```

### 6. Cross-Database Queries

**You can say:**
```
"Compare the user count between database1 and database2"
"Show me all tables that have 'user' in their name across all databases"
```

**Claude will execute:**
```sql
SELECT
  (SELECT COUNT(*) FROM database1.users) as db1_users,
  (SELECT COUNT(*) FROM database2.users) as db2_users;

SELECT TABLE_SCHEMA, TABLE_NAME
FROM information_schema.TABLES
WHERE TABLE_NAME LIKE '%user%';
```

## What Operations Are Blocked?

### DELETE Operations (Blocked by default)
```
❌ "Delete all old logs"
❌ "Remove user with id 5"

To enable: Set ALLOW_DELETE=true in ~/.config/claude/mysql-mcp/.env
```

### DDL Operations (Blocked by default)
```
❌ "Create a new table called products"
❌ "Add a new column to the users table"
❌ "Drop the temporary_data table"

To enable: Set ALLOW_DDL=true in ~/.config/claude/mysql-mcp/.env
```

## Real-World Usage Examples

### Example 1: Data Analysis
```
You: "Analyze the user registration trend for the last 30 days"

Claude will run:
SELECT
  DATE(created_at) as registration_date,
  COUNT(*) as new_users
FROM users
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(created_at)
ORDER BY registration_date;
```

### Example 2: Data Validation
```
You: "Check for any duplicate emails in the users table"

Claude will run:
SELECT email, COUNT(*) as count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

### Example 3: Reporting
```
You: "Generate a summary of sales by product category for this month"

Claude will run:
SELECT
  p.category,
  COUNT(o.id) as total_orders,
  SUM(o.quantity) as units_sold,
  SUM(o.total_price) as revenue
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE MONTH(o.created_at) = MONTH(CURRENT_DATE())
  AND YEAR(o.created_at) = YEAR(CURRENT_DATE())
GROUP BY p.category
ORDER BY revenue DESC;
```

### Example 4: Data Migration
```
You: "Copy all active users from the staging database to production"

Claude will run:
INSERT INTO production.users (name, email, status, created_at)
SELECT name, email, status, created_at
FROM staging.users
WHERE status = 'active';
```

## Tips for Best Results

1. **Be specific about the database**:
   - Good: "Query the users table in beasiswa_core"
   - Better: "Show me all active users from beasiswa_core.users"

2. **Specify limits for large tables**:
   - Good: "Show me data from the logs table"
   - Better: "Show me the latest 100 entries from the logs table"

3. **Use natural language**:
   - Claude understands context and will translate your request to SQL
   - You don't need to write SQL yourself

4. **Ask for explanations**:
   - "Show me the user count and explain what each status means"
   - Claude will run the query and provide context

## Testing the Connection

To verify your MCP is working, try these simple commands:

1. **Test connection**:
   ```
   "Show me the MySQL version"
   ```
   Claude executes: `SELECT VERSION();`

2. **List databases**:
   ```
   "What databases do I have access to?"
   ```
   Claude executes: `SHOW DATABASES;`

3. **Check permissions**:
   ```
   "What are my MySQL privileges?"
   ```
   Claude executes: `SHOW GRANTS FOR CURRENT_USER();`

## Remember

- The MCP server is already configured and running
- It works across ALL your Claude Code projects
- Credentials are safely stored in `~/.config/claude/mysql-mcp/.env`
- DELETE and DDL operations are blocked by default for safety