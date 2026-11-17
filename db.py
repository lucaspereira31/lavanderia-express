import os
import ssl
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    # Configura o contexto SSL exigido pelo Aiven sem depender de arquivo ca.pem local
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "defaultdb"),
        port=int(os.getenv("DB_PORT", 3306)),
        ssl=ssl_context,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        connect_timeout=10
    )