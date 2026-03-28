import random
import time
from cloud.upload_to_thingspeak import send_data

def generate_data():
    return {
        "bin1": random.randint(0, 100),
        "bin2": random.randint(0, 100),
        "bin3": random.randint(0, 100)
    }

if __name__ == "__main__":
    while True:
        data = generate_data()
        print("Generated:", data)

        send_data(data)

        time.sleep(15)  # ThingSpeak limit