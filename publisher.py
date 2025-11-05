import random
import time
from datetime import datetime
from db import connect_db, init_db
from mqtt_config import create_client, topic

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
        kelembapan = round(random.uniform(40, 70), 2)
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        payload = f"{waktu},{suhu},{tekanan},{kelembapan}"
        client.publish(topic, payload)
        print(f"📤 Published: {payload}")

        sql = "INSERT INTO sensor_data (waktu, suhu, tekanan, kelembapan) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (waktu, suhu, tekanan, kelembapan))
        conn.commit()

        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 Dihentikan oleh user.")
    client.loop_stop()
    cursor.close()
    conn.close()
