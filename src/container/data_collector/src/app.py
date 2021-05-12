from domain_registrar_collector import GoDaddyCollector
import os

print("Hello World", os.getenv("POSTGRES_DB"), os.getenv("POSTGRES_USER"), os.getenv("POSTGRES_PASSWORD"))

if __name__ == "__main__":
    from time import sleep

    sleep(2)

    from psycopg2 import connect
    from psycopg2.extras import RealDictCursor
    conn = connect(
        host="database",
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("DB_PORT", 5432),
        # sslmode='verify-ca',
        # sslrootcert="./root.crt"
    )
    

    gd_collector = GoDaddyCollector()

    gd_collector.gather()
    gd_collector.upload_to_db(conn)