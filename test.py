import requests
import json
with open('./config.json', 'r') as file:
    config = json.load(file)
response = requests.post(f"http://localhost:5000/config", json=config['others']['10.10.1.1'])
print(response)
