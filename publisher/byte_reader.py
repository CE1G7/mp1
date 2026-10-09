import hashlib

FIRMWARE_VERSION = 1.0
FIRMWARE_SIZE = None
NUM_CHUNKS = 4
MERKLE_ROOT = None
FIRMWARE_SIZE = None
#Read txt file as bytes
with open("firmware.txt", "rb") as f:
    bytes = f.read()

FIRMWARE_SIZE = len(bytes)

#Handle depending if bytes are divisible by 4
r = len(bytes) % NUM_CHUNKS
chunk_sizes = []
if not(r == 0):
    base = int(len(bytes) / NUM_CHUNKS)
    for i in range (0,NUM_CHUNKS):
        chunk_sizes.append(base)
    for i in range(0,r):
        chunk_sizes[i]+=1
else:
    size = int(len(bytes)/NUM_CHUNKS)
    for i in range(0,NUM_CHUNKS):
        chunk_sizes.append(size)

# Assign bytes to chunks
chunks = []
start = 0
for i in range (0,4):
    chunk = bytes[start:start+chunk_sizes[i]]
    chunks.append(chunk)
    start+=chunk_sizes[i]

#construct leaves
leaves = []
for chunk in chunks:
    leaves.append(hashlib.sha256(chunk).digest())

#build tree
p0 = hashlib.sha256(leaves[0]+leaves[1]).digest()
p1 = hashlib.sha256(leaves[2]+leaves[3]).digest()
p2 = hashlib.sha256(p0+p1).digest()

MERKLE_ROOT = p2
with open("manifest.txt","w") as f:
    manifest_contents = (
    f"FIRMWARE_VERSION: {FIRMWARE_VERSION}\nFIRMWARE_SIZE: {FIRMWARE_SIZE}\n"
    f"NUM_CHUNKS: {NUM_CHUNKS}\nMERKLE_ROOT: {MERKLE_ROOT}\n"
    f"CHUNKS: [\nC0: {{INDEX: 0, FILENAME: C0}},\nC1: {{INDEX: 1, FILENAME: C1}},\nC2: {{INDEX: 2, FILENAME: C2}},\nC3: {{INDEX: 3, FILENAME: C3}}\n]")
    f.write(manifest_contents)

for c in chunks:
    print(f"chunk")
    c = list(c)
    for i in range(0,len(c)):
        print(c[i])