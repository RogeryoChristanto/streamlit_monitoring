import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

# --- Membaca file .env ---
load_dotenv()

# --- Ambil variabel dari .env ---
broker = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))
topic = os.getenv("MQTT_TOPIC")

def create_client():
    """Membuat koneksi MQTT Client"""
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.connect(broker, port)
    print(f"✅ Terhubung ke broker MQTT: {broker}:{port}")
    return client
