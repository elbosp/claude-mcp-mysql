#!/usr/bin/env python3
"""MySQL MCP Server for Claude Code - DML operations only"""

import os
import sys
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class MySQLMCPServer:
    def __init__(self):
        self.connection = None
        self.host = os.getenv('MYSQL_HOST', '127.0.0.1')
        self.port = os.getenv('MYSQL_PORT', '3306')
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.database = os.getenv('MYSQL_DATABASE', None)
        self.allow_delete = os.getenv('ALLOW_DELETE', 'false').lower() == 'true'
        self.allow_ddl = os.getenv('ALLOW_DDL', 'false').lower() == 'true'

    def connect(self):
        """Establish MySQL connection"""
        try:
            connection_params = {
                'host': self.host,
                'port': int(self.port),
                'user': self.user,
                'password': self.password
            }

            # Add database if specified
            if self.database:
                connection_params['database'] = self.database

            self.connection = mysql.connector.connect(**connection_params)
            sys.stderr.write(f"MySQL connected to {self.host}:{self.port} as {self.user}\n")
            return True
        except Error as e:
            sys.stderr.write(f"MySQL connection failed: {e}\n")
            return False

    def handle_initialize(self, request):
        """Handle initialize request"""
        if not self.connect():
            return {"error": "Failed to connect to MySQL"}

        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "mysql-mcp-server",
                "version": "1.0.0"
            }
        }

    def handle_list_tools(self, request):
        """Handle tools/list request"""
        return {
            "tools": [
                {
                    "name": "query",
                    "description": "Execute MySQL query (SELECT, INSERT, UPDATE only - DELETE is blocked)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute"
                            },
                            "database": {
                                "type": "string",
                                "description": "Database to use (optional)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        }

    def handle_tool_call(self, request):
        """Handle tool call"""
        params = request.get('params', {})
        name = params.get('name')
        arguments = params.get('arguments', {})

        if name == 'query':
            return self.execute_query(arguments)

        return {"error": f"Unknown tool: {name}"}

    def execute_query(self, arguments):
        """Execute MySQL query"""
        query = arguments.get('query')
        database = arguments.get('database')

        if not query:
            return {"error": "No query provided"}

        query_upper = query.upper().strip()

        # Check DDL operations
        ddl_keywords = ['CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'RENAME']
        if not self.allow_ddl and any(query_upper.startswith(kw) for kw in ddl_keywords):
            return {"error": "DDL operations are not allowed. Only DML operations are permitted."}

        # Check DELETE operations
        if not self.allow_delete and query_upper.startswith('DELETE'):
            return {"error": "DELETE operations are not allowed. Only SELECT, INSERT, and UPDATE are permitted."}

        try:
            cursor = self.connection.cursor()

            # Use database if specified
            if database:
                cursor.execute(f"USE {database}")

            # Execute query
            cursor.execute(query)

            # Fetch results for SELECT queries
            if query_upper.startswith('SELECT') or query_upper.startswith('SHOW'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                # Format results as list of dicts
                formatted_results = []
                for row in results:
                    formatted_results.append(dict(zip(columns, row)))

                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(formatted_results, indent=2, default=str)
                    }]
                }
            else:
                # For INSERT, UPDATE, DELETE
                self.connection.commit()
                affected_rows = cursor.rowcount
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Query executed successfully. Affected rows: {affected_rows}"
                    }]
                }

        except Error as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }]
            }
        finally:
            if cursor:
                cursor.close()

    def handle_request(self, request):
        """Route request to appropriate handler"""
        method = request.get('method')

        if method == 'initialize':
            return self.handle_initialize(request)
        elif method == 'tools/list':
            return self.handle_list_tools(request)
        elif method == 'tools/call':
            return self.handle_tool_call(request)
        elif method == 'shutdown':
            if self.connection:
                self.connection.close()
            return {}
        else:
            return {"error": f"Unknown method: {method}"}

    def run(self):
        """Main loop - read JSON-RPC from stdin, write to stdout"""
        sys.stderr.write("MySQL MCP Server started\n")

        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": self.handle_request(request)
                }
                print(json.dumps(response))
                sys.stdout.flush()

            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                sys.stderr.write(f"Error: {str(e)}\n")

if __name__ == "__main__":
    server = MySQLMCPServer()
    server.run()