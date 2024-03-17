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
secret_key = None

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
    global secret_key
    print("aggregator start")
    app.register_blueprint(aggregator.aggregator_bp)
    with open('./config.json', 'r') as file:
        aggregator.config = json.load(file)

    aggregator.iterations = aggregator.config["aggregator"]["iteration"]
    
    context = tenseal.context(
            tenseal.SCHEME_TYPE.ckks,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
            )

    context.generate_galois_keys()
    context.global_scale = 2**40

    aggregator.context = context

    private_context = context.serialize()
    
    secret_key = context.secret_key()
    context.make_context_public()
    public_context = context.serialize()

    with open("./private_context.pkl", "wb") as f:
        f.write(private_context)

    with open("./public_context.pkl", "wb") as f:
        f.write(public_context)
 
 # call the others
    #print(aggregator.config)
    for key, value in aggregator.config['others'].items():
        print(key, value)
        try:
            if value["type"] == "client":
                with open("./private_context.pkl", "rb") as f:
                    files = {"file": ("./private_key.pkl", f.read())}
                    requests.post(f"http://{key}:5000/setup_context", files=files)
            elif value["type"] == "switch":
                with open("./public_context.pkl", "rb") as f:
                    files = {"file": ("./public_key.pkl", f.read())}
                    requests.post(f"http://{key}:5000/setup_context", files=files)

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
