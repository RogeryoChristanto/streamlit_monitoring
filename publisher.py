import random
import time
from datetime import datetime
from db import connect_db, init_db
from mqtt_config import create_client, topic
import mysql.connector
import os
from dotenv import load_dotenv

# PENTING: Panggil load_dotenv() di sini
# Ini akan memuat file .env Anda
load_dotenv()

def connect_db():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=os.getenv("MYSQL_PORT"),      # <-- TAMBAHAN PENTING
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASS"),
            database=os.getenv("MYSQL_DB")
        )
        print("✅ Berhasil terhubung ke Database Railway!")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ GAGAL terhubung ke Database: {err}")
        return None

def init_db():
    # Fungsi ini mungkin Anda gunakan untuk membuat tabel,
    # Jika Anda sudah membuatnya di Railway, Anda bisa biarkan ini kosong
    pass

# --- Tidak ada perubahan lain yang diperlukan di publisher.py ---

# Inisialisasi database dan MQTT
init_db()
client = create_client()
client.loop_start()

conn = connect_db()
cursor = conn.cursor()

print("🚀 IoT Publisher berjalan... (mengirim data setiap 2 detik)\n")

try:
    while True:
        suhu = round(random.uniform(25, 35), 2)
        tekanan = round(random.uniform(1000, 1020), 2)
        kelembaban = round(random.uniform(40, 70), 2)
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        payload = f"{waktu},{suhu},{tekanan},{kelembaban}"
        client.publish(topic, payload)
        print(f"📤 Published: {payload}")

        sql = "INSERT INTO sensor_data (waktu, suhu, tekanan, kelembaban) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (waktu, suhu, tekanan, kelembaban))
        conn.commit()

        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 Dihentikan oleh user.")
    client.loop_stop()
    cursor.close()
    conn.close()
