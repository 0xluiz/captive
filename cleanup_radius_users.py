import mysql.connector
from config import Config
from datetime import datetime

def cleanup_expired_users():
    conn = mysql.connector.connect(
        host=Config.RADIUS_DB_HOST,
        database=Config.RADIUS_DB_NAME,
        user=Config.RADIUS_DB_USER,
        password=Config.RADIUS_DB_PASSWORD
    )
    cursor = conn.cursor()

    # Find expired users
    query_select = """
    SELECT username FROM radcheck
    WHERE attribute='Expiration' AND value < %s
    """
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(query_select, (now,))
    expired_users = cursor.fetchall()

    # Delete expired users from radcheck
    for user in expired_users:
        username = user[0]
        query_delete = "DELETE FROM radcheck WHERE username=%s"
        cursor.execute(query_delete, (username,))

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    cleanup_expired_users()
