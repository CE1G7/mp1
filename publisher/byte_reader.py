import hashlib
import json


class MerkleTree:
    def __init__(self):
        self.FIRMWARE_VERSION = 1.0
        self.FIRMWARE_SIZE = None
        self.NUM_CHUNKS = 4
        self.MERKLE_ROOT = None
        self.FIRMWARE_SIZE = None
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