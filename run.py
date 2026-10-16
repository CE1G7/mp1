import os, socket, subprocess, sys, time, venv

ENV = '''
BROKER_IP=127.0.0.1
BROKER_PORT=1883

MANIFEST_TOPIC=mp1/ota_update/manifest
FIRMWARE_TOPIC=mp1/ota_update/firmware

MQTT_USERNAME=user
MQTT_PASSWORD=asdf
'''

ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(ROOT, "venv")
REQUIREMENTS = ["paho-mqtt", "dotenv"]

def venv_python():
    sub = "Scripts" if os.name == "nt" else "bin"
    exe = "python.exe" if os.name == "nt" else "python"
    return os.path.join(VENV_DIR, sub, exe)

def wait_for_broker(host="localhost", port=1883, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("Broker did not start")

def create_env_file():
    if not os.path.isfile(".env"):
        with open(".env", "wt") as f:
            f.write(ENV)

def main():
    os.chdir(ROOT)
    create_env_file()

    # 1. Start the broker
    subprocess.check_call(["docker", "compose", "up", "-d"])

    try:
        # 2. Create the venv (skipped if it already exists)
        if not os.path.exists(venv_python()):
            venv.create(VENV_DIR, with_pip=True)

        # 3. Install dependencies into the venv
        py = venv_python()
        subprocess.check_call([py, "-m", "pip", "install", "-q", *REQUIREMENTS])

        # 4. Wait for the broker, then start client first, then server
        wait_for_broker()
        client = subprocess.Popen([py, "ota_client.py"])
        time.sleep(1)
        server = subprocess.Popen([py, "ota_server.py"])

        server.wait()
        client.wait(timeout=60)
        print("Client exit code:", client.returncode)
    finally:
        # 5. Stop the broker
        subprocess.run(["docker", "compose", "down"])

if __name__ == "__main__":
    main()
