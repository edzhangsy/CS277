from flask import Flask, request, jsonify, Blueprint, current_app
import sys
import json
import requests
import switch
import aggregator
import client
import tenseal

app = Flask(__name__)

# the current_bp store the pointer to the current blueprint
current_type = None

@app.route("/config", methods=['POST'])
def config():
    # this interface will get a json dictionary from the server
    # should set up the encrypter, resolver, etc.
    config = request.json
    global current_type
    config_type = config.get("type")
    print(config_type)
    if config_type == 'client':
        current_type = client
    elif config_type == 'switch':
        current_type = switch
    current_type.config = config
    current_type.init(config)
    return "config transported"
    
@app.route("/log", methods=['GET'])
def log():
    # add some guard here to guard current_type == None
    global current_type
    return current_type.log

def aggregator_init():
    print("aggregator start")
    app.register_blueprint(aggregator.aggregator_bp)
    with open('./config.json', 'r') as file:
        aggregator.config = json.load(file)

    aggregator.iterations = aggregator.config["aggregator"]["iteration"]
 
 # call the others
    print(aggregator.config)
    for key, value in aggregator.config['others'].items():
        print(key, value)
        try:
            response = requests.post(f"http://{key}:5000/config", json=value, timeout=0.5)
            print(f"http://{key}:5000/config")
            print(response)
        except requests.exceptions.ConnectTimeout:
            print(f"http://{key}:5000/config timeout")

    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        aggregator_init()
    app.register_blueprint(switch.switch_bp)
    app.register_blueprint(client.client_bp)
    app.run('0.0.0.0', debug=True, port=5000)
    for key, value in config["others"].items():
        if value["type"] == "client":
            requests.get(f"http://{key}/train")
