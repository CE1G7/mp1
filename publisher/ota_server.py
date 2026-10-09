import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import struct
from byte_reader import MerkleTree

load_dotenv('../.env')

BROKER = os.getenv('BROKER_IP')
PORT = int(os.getenv('BROKER_PORT'))
TOPIC = os.getenv('UPDATE_TOPIC')

USERNAME = os.getenv('MQTT_USERNAME')
PASSWORD = os.getenv('MQTT_PASSWORD')

tree = MerkleTree()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)

def publish(payload: str,topic: str):
    try:
        info = client.publish(topic, payload, qos=2)
        info.wait_for_publish(timeout=10)
    except Exception as e:
        print("connection failed", e)
def main():
    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print("Connection failed:", e)
    client.loop_start()
    while(True):
        message = input("\nEnter message:")
        if(message == "exit"):
            break
        elif(message == "firmware"):
            chunks = tree.get_chunks()
            indexed_chunks = []
            for i,chunk in enumerate(chunks):
                indexed_chunks.append(bytes([i])+struct.pack("<H",round(tree.FIRMWARE_VERSION*100))+chunk)
            for c in indexed_chunks:
                publish(c,"mp1/ota_update")
            manifest = tree.get_manifest()
            publish(manifest,"mp1/ota_update")

        else:
            publish(message, "mp1/ota_update")
    client.disconnect()
    client.loop_stop()

if __name__ == "__main__":
    main()
