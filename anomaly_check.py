from db import connect_db
import time

def detect_anomaly():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    print("🔍 Sistem deteksi anomali aktif...\n")

    while True:
        cursor.execute("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1")
        data = cursor.fetchone()
        if data:
            suhu = data['suhu']
            kelembapan = data['kelembapan']

            if suhu > 33 or kelembapan < 45:
                print(f"⚠️ Anomali Terdeteksi! Suhu: {suhu}°C | Kelembapan: {kelembapan}%")
        time.sleep(3)

if __name__ == "__main__":
    detect_anomaly()
