import threading, os, json, struct, sys
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from update import Update
from time import sleep


load_dotenv('../.env')

BROKER = os.getenv('BROKER_IP')
PORT = int(os.getenv('BROKER_PORT'))
MANIFEST_TOPIC = os.getenv('MANIFEST_TOPIC')
FIRMWARE_TOPIC = os.getenv('FIRMWARE_TOPIC')

USERNAME = os.getenv('MQTT_USERNAME')
PASSWORD = os.getenv('MQTT_PASSWORD')

update = Update()

def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected to MQTT Broker with code {rc}")
    try:
        client.subscribe([(MANIFEST_TOPIC, 2), (FIRMWARE_TOPIC, 2)])
        print(f"Subscribed.")
    except Exception as e:
        print(f"Error: {e}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"\n{msg.topic} -> {payload}")

def on_firmware_chunk(client, userdata, msg):
    payload = msg.payload
    print(f"Chunk reveived: {payload}")
    update.add_chunk(payload)


def on_manifest(client, userdata, msg):
    update.manifest = json.loads(msg.payload)
    print(f"Update manifest received for v{update.manifest["FIRMWARE_VERSION"]}:\n{update.manifest}")
    sleep(1)
    if update.verify():
        update.apply()
    else:
        for i in range(5):
            print(f"Update verfication failed. Retrying in 30s ({i+1}/5).")
            sleep(30)
            if update.verify():
                update.apply()
                break



def start_mqtt_listener():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.message_callback_add(MANIFEST_TOPIC, on_manifest)
    client.message_callback_add(FIRMWARE_TOPIC, on_firmware_chunk)
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
