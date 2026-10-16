import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import struct, hashlib, json, os
from time import sleep


load_dotenv('.env')

BROKER = os.getenv('BROKER_IP')
PORT = int(os.getenv('BROKER_PORT'))
MANIFEST_TOPIC = os.getenv('MANIFEST_TOPIC')
FIRMWARE_TOPIC = os.getenv('FIRMWARE_TOPIC')

USERNAME = os.getenv('MQTT_USERNAME')
PASSWORD = os.getenv('MQTT_PASSWORD')


class MerkleTree:
    def __init__(self):
        self.FIRMWARE_VERSION = 1.0
        self.FIRMWARE_SIZE = None
        self.NUM_CHUNKS = 4
        self.MERKLE_ROOT = None
        self.CHUNKS = []
        self.LEAVES = []
        self.MANIFEST = None

        #Read txt file as bytes
        with open("firmware.txt", "rb") as f:
            bytes = f.read()

        self.FIRMWARE_SIZE = len(bytes)

        #Handle depending if bytes are divisible by 4
        r = len(bytes) % self.NUM_CHUNKS
        chunk_sizes = []
        if not(r == 0):
            base = int(len(bytes) / self.NUM_CHUNKS)
        for i in range (0, self.NUM_CHUNKS):
            chunk_sizes.append(base)
        for i in range(0,r):
            chunk_sizes[i]+=1
        else:
            size = int(len(bytes)/ self.NUM_CHUNKS)
            for i in range(0, self.NUM_CHUNKS):
                chunk_sizes.append(size)
        # Assign bytes to chunks
        start = 0
        for i in range (0,4):
            chunk = bytes[start:start+chunk_sizes[i]]
            self.CHUNKS.append(chunk)
            start+=chunk_sizes[i]

        #construct leaves
        for chunk in self.CHUNKS:
            self.LEAVES.append(hashlib.sha256(chunk).digest())

        #build tree
        p0 = hashlib.sha256(self.LEAVES[0]+self.LEAVES[1]).digest()
        p1 = hashlib.sha256(self.LEAVES[2]+self.LEAVES[3]).digest()
        p2 = hashlib.sha256(p0+p1).digest()

        self.MERKLE_ROOT = p2

        manifest = {
            "FIRMWARE_VERSION" : self.FIRMWARE_VERSION,
            "FIRMWARE_SIZE": self.FIRMWARE_SIZE,
            "NUM_CHUNKS": self.NUM_CHUNKS,
            "MERKE_ROOT": self.MERKLE_ROOT.hex(),
            "CHUNKS": [{"INDEX": i, "FILENAME": f"C{i}"} for i in range(len(self.CHUNKS))]
        }
        self.MANIFEST = json.dumps(manifest)
    def get_chunks(self):
        return self.CHUNKS
    def get_manifest(self):
        return self.MANIFEST
    def get_merkle_root(self):
        return self.MERKLE_ROOT


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
    sleep(1)
    chunks = tree.get_chunks()
    indexed_chunks = []
    for i,chunk in enumerate(chunks):
        indexed_chunks.append(bytes([i])+struct.pack("<H",round(tree.FIRMWARE_VERSION*100))+chunk)
    for c in indexed_chunks:
        publish(c, FIRMWARE_TOPIC)
    manifest = tree.get_manifest()
    publish(manifest, MANIFEST_TOPIC)
    sleep(3)
    client.disconnect()
    client.loop_stop()


if __name__ == "__main__":
    main()
