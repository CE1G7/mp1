import threading, os, json, struct, sys, hashlib
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from time import sleep


load_dotenv('.env')

BROKER = os.getenv('BROKER_IP')
PORT = int(os.getenv('BROKER_PORT'))
MANIFEST_TOPIC = os.getenv('MANIFEST_TOPIC')
FIRMWARE_TOPIC = os.getenv('FIRMWARE_TOPIC')

USERNAME = os.getenv('MQTT_USERNAME')
PASSWORD = os.getenv('MQTT_PASSWORD')


class Update:
    def __init__(self):
        self.received_chunks = []
        self.ordered_chunks = []
        self.manifest = None
        self.merkel_root = None
        self.update_valid = False
        self.update = None

    def add_chunk(self, chunk):
        self.received_chunks.append(chunk)

    def verify(self):
        print("Verifying update...")
        self.order_chunks()
        for i, chunk in enumerate(self.ordered_chunks):
            if chunk == None:
                print(f"Chunk {i} missing.")
                return False
        print(f"Calculated merkel root: {self.calculate_merkel_root()}")
        if self.merkel_root != self.manifest["MERKE_ROOT"]:
            print("Mismatched merkel root.")
            return False
        print("Merkel root match.")
        try:
            self.update = b"".join(self.ordered_chunks)
        except Exception as e:
            print(f"Failed to join chunks: {e}")
        if len(self.update) != self.manifest["FIRMWARE_SIZE"]:
            print("Missmatched update size.")
            return False
        print("Update size match.")
        self.update_valid = True
        return True

    def order_chunks(self):
        num_chunks = int(self.manifest["NUM_CHUNKS"])
        fw_ver = self.manifest["FIRMWARE_VERSION"]
        ordered_chunks = [None] * num_chunks
        if len(self.received_chunks) >= num_chunks:
            print("Numer of chunks OK")
            for chunk in self.received_chunks:
                try:
                    index, v_raw = struct.unpack("<BH", chunk[:3])
                    version = v_raw / 100
                    data = chunk[3:]
                    if version == fw_ver:
                        ordered_chunks[int(index)] = data
                    else:
                        print(f"Skipping chunk with invalid version ({version}): {chunk}")
                except Exception as e:
                    print(f"Skipping invalid chunk: {chunk} {e}")
                    continue
            print(f"Ordered chunks: {ordered_chunks}")
            self.ordered_chunks = ordered_chunks
            return ordered_chunks
        return []

    def calculate_merkel_root(self):
        #construct leaves
        leaves = []
        for chunk in self.ordered_chunks:
            leaves.append(hashlib.sha256(chunk).digest())
        #build tree
        p0 = hashlib.sha256(leaves[0]+leaves[1]).digest()
        p1 = hashlib.sha256(leaves[2]+leaves[3]).digest()
        p2 = hashlib.sha256(p0+p1).digest()
        merkel_root = p2.hex()
        self.merkel_root = merkel_root
        return merkel_root

    def apply(self):
        if self.update_valid:
            print("Applying update.")
            try:
                with open("firmware_reconstructed.txt", "wb") as f:
                    f.write(self.update)
                print("Update complete!")
                return True
            except Exception as e:
                print(f"Update failed: {e}")
        return False


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
    sys.exit() # So run.py can exit


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
