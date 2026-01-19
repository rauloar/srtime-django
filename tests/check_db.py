
import pymysql
from sqlalchemy.engine.url import make_url

try:
    from backend.database import settings
    url = make_url(settings.DB_URL)
    user = url.username or 'root'
    password = url.password or ''
    host = url.host or 'localhost'
    port = url.port or 3306
    db_name = url.database or 'zk_webapp'

    conn = pymysql.connect(user=user, password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
    result = cursor.fetchone()
    print(f"Database Found: {result}")
except Exception as e:
    print(f"Error: {e}")
