# Updated version of the config.py file for connecting to a PostgreSQL database

import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",  # Update with your actual host, e.g., "localhost" or an IP address
        database="health",  # Update with your actual database name
        user="postgres",  # Update with your actual database user
        password="phu220103", # Update with your actual database password
        port='8888'
    )
    return conn