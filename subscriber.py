import threading
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv


load_dotenv('.env')

BROKER = os.getenv('BROKER_IP')
PORT = int(os.getenv('BROKER_PORT'))
TOPIC = os.getenv('UPDATE_TOPIC')

USERNAME = os.getenv('MQTT_USERNAME')
PASSWORD = os.getenv('MQTT_PASSWORD')


def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected to MQTT Broker with code {rc}")
    try:
        client.subscribe(TOPIC, qos=2)
        print(f"Subscribed to topic: {TOPIC}")
    except Exception as e:
        print(f"Error: {e}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"\n{msg.topic} -> {payload}")


def start_mqtt_listener():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(USERNAME, PASSWORD)
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
        print("MQTT listener started")
    except Exception as e:
        print("Connection failed:", e)


if __name__ == "__main__":
    try:
        start_mqtt_listener()
    except KeyboardInterrupt:
        sys.exit()
