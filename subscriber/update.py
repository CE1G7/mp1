import hashlib, json, struct

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






