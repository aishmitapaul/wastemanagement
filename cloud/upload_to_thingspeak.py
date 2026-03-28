import requests
from utils.config import WRITE_API_KEY

def send_data(data):
    url = "https://api.thingspeak.com/update"

    payload = {
        "api_key": WRITE_API_KEY,
        "field1": data["bin1"],
        "field2": data["bin2"],
        "field3": data["bin3"]
    }

    response = requests.get(url, params=payload)

    if response.status_code == 200:
        print("Data sent to cloud")
    else:
        print("Error sending data")