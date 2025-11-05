import mysql.connector
from dotenv import load_dotenv
import os

# Membaca file .env
load_dotenv()

def connect_db():
    """Koneksi ke database MySQL"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASS"),
            database=os.getenv("MYSQL_DB")
        )
        return conn
    except Exception as e:
        print("❌ Gagal konek ke database:", e)
        exit()

def init_db():
    """Membuat tabel sensor_data jika belum ada"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            waktu DATETIME,
            suhu FLOAT,
            tekanan FLOAT,
            kelembapan FLOAT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
