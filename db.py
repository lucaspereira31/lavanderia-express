import os
import ssl
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    # Cria contexto SSL para conexão segura com o Aiven
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
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )