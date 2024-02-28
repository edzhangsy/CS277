from flask import Flask, request, jsonify, Blueprint, current_app
import sys
import json
import requests
import switch
import aggregator
import client

app = Flask(__name__)

# the current_bp store the pointer to the current blueprint
current_type = NULL
current_bp = NULL

@route("/config", methods=['POST'])
def config():
    # this interface will get a json dictionary from the server
    # should set up the encrypter, resolver, etc.
    config = request.json
    print(config)
    config_type = config.get("type")
    if current_bp != NULL:
        app.blueprint.pop(current_bp)

    if config_type == 'client':
        current_type = client
        current_bp = client.client_bp
    elif config_type == 'switch':
        current_type = switch
        current_bp = switch.switch_bp
    current_type.config = config
    current_type.init(config)
    app.register_blueprint(current_bp)
    return "config transported"
    
@route("/log", methods=['GET'])
def log():
    return current_type.log

def aggregator_init():
    print("aggregator start")
    app.register_blueprint(aggregator.aggregator_bp)
    with open('./config.json', 'r') as file:
        config = json.load(file)
    # call the others
    for key, value in config['others']:
        response = requests.post("http://{key}/config", data=value)

    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        aggregator_init()
    app.run(debug=True)
