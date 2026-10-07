import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os


load_dotenv('.env')

BROKER = os.getenv('BROKER_IP')
PORT = int(os.getenv('BROKER_PORT'))
TOPIC = os.getenv('UPDATE_TOPIC')

USERNAME = os.getenv('MQTT_USERNAME')
PASSWORD = "buh" #os.getenv('MQTT_PASSWORD')


def publish(payload: str):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(USERNAME, PASSWORD)
    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print("Connection failed:", e)
    client.publish(TOPIC, payload, qos=2)
    client.disconnect()


while(True):
    message = input("\nEnter message:")
    if(message == "exit"):
        break
    publish(message)
