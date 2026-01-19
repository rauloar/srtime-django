
import pymysql

def create_database():
    try:
        # Connect to MySQL Server (assuming default WampServer: root, no password)
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with connection.cursor() as cursor:
                # Create database if not exists
                sql = "CREATE DATABASE IF NOT EXISTS zk_webapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                cursor.execute(sql)
                print("✅ Database 'zk_webapp' created or already exists.")
        finally:
            connection.close()
            
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("Please ensure WampServer is running and the user 'root' has no password (default) or provide credentials.")

if __name__ == "__main__":
    def create_database():
        import pymysql
        from sqlalchemy.engine.url import make_url
        try:
            from backend.database import settings
            url = make_url(settings.DB_URL)
            host = url.host or 'localhost'
            user = url.username or 'root'
            password = url.password or ''
            port = url.port or 3306
            db_name = url.database or 'zk_webapp'

            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                port=port
            )
            with connection.cursor() as cursor:
                sql = f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                cursor.execute(sql)
                connection.commit()
                print(f"✅ Database '{db_name}' created or already exists.")
        except Exception as e:
            print(f"❌ Error creating database: {e}")
