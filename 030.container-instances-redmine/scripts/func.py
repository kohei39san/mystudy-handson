import io
import json
import logging
import os
import mysql.connector
from fdk import response

def handler(ctx, data: io.BytesIO = None):
    logging.getLogger().setLevel(logging.INFO)
    
    try:
        # Get configuration from environment variables
        mysql_host = os.environ.get('MYSQL_HOST')
        mysql_port = int(os.environ.get('MYSQL_PORT', '3306'))
        mysql_admin_user = os.environ.get('MYSQL_ADMIN_USER')
        mysql_admin_password = os.environ.get('MYSQL_ADMIN_PASSWORD')
        redmine_db_password = os.environ.get('REDMINE_DB_PASSWORD')
        
        # Connect to MySQL
        connection = mysql.connector.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_admin_user,
            password=mysql_admin_password
        )
        
        cursor = connection.cursor()
        
        # Create database and user for Redmine
        cursor.execute("CREATE DATABASE IF NOT EXISTS redmine CHARACTER SET utf8mb4")
        cursor.execute("CREATE USER IF NOT EXISTS 'redmine'@'%' IDENTIFIED BY %s", (redmine_db_password,))
        cursor.execute("GRANT ALL PRIVILEGES ON redmine.* TO 'redmine'@'%'")
        cursor.execute("FLUSH PRIVILEGES")
        
        cursor.close()
        connection.close()
        
        logging.info("MySQL database and user created successfully")
        return response.Response(
            ctx, response_data=json.dumps({"status": "success", "message": "Database initialized"}),
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logging.error(f"Error initializing database: {str(e)}")
        return response.Response(
            ctx, response_data=json.dumps({"status": "error", "message": str(e)}),
            headers={"Content-Type": "application/json"},
            status_code=500
        )