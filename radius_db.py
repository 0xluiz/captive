import mysql.connector
from config import Config
from datetime import datetime, timedelta

def get_db_connection():
    connection = mysql.connector.connect(
        host=Config.RADIUS_DB_HOST,
        database=Config.RADIUS_DB_NAME,
        user=Config.RADIUS_DB_USER,
        password=Config.RADIUS_DB_PASSWORD
    )
    return connection

def add_user_to_radius(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert user credentials into radcheck table
    query = """
    INSERT INTO radcheck (username, attribute, op, value)
    VALUES (%s, 'Cleartext-Password', ':=', %s)
    """
    cursor.execute(query, (username, password))

    # Set account expiration time (e.g., 8 hours from now)
    expire_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%b %d %Y %H:%M:%S')
    query_expire = """
    INSERT INTO radcheck (username, attribute, op, value)
    VALUES (%s, 'Expiration', ':=', %s)
    """
    cursor.execute(query_expire, (username, expire_time))

    conn.commit()
    cursor.close()
    conn.close()

