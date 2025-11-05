import paho.mqtt.client as mqtt
from mqtt_config import broker, port, topic

def on_message(client, userdata, message):
    print("📩 Pesan diterima:", message.payload.decode())

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message

client.connect(broker, port)
client.subscribe(topic)
print(f"🕓 Menunggu pesan pada topik '{topic}'...\n")

client.loop_forever()
