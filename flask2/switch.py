from flask import Blueprint, current_app
import ast
#import tenseal
import requests

switch_bp = Blueprint('switch', __name__)

log = {}
config = {}
#context = None
address = None
received_file_count = 0


def init(config):
    #global context
    global address
    #global config

    #context = config["context"]
    address = config["send"]

    return

@switch_bp.route("/", methods=["POST"])
def add():
    global address
    global config
    
    # Get files
    file = request.files["file"]
    file.save(f"{file.filename}")

    received_file_count += 1

    recieve_address = config["receive"]

    if received_file_count == 8:
        # Open files and get weights
        receive1 = receive_address[0]
        receive2 = receive_address[1]
        for i in range(4):
            with open(f"../mnist_model/weights/{receive1}_torch_weights"+str(i)+".json", "r") as json_file:
                if i == 0:
                    weight0 = ast.literal_eval(json_file.read())
                elif i == 1:
                    bias0 = ast.literal_eval(json_file.read())
                elif i == 2:
                    weight1 = ast.literal_eval(json_file.read())
                elif i == 3:
                    bias1 = ast.literal_eval(json_file.read())

        for i in range(4):
            with open(f"../mnist_model/weights/{receive2}_torch_weights"+str(i)+".json", "r") as json_file:
                if i == 1:
                    weight2 = ast.literal_eval(json_file.read())
                elif i == 2:
                    bias2 = ast.literal_eval(json_file.read())
                elif i == 3:
                    weight3 = ast.literal_eval(json_file.read())
                elif i == 4:
                    bieas3 = ast.literal_eval(json_file.read())

        add_results = {
            0: result0,
            1: result1,
            2: result2,
            3: result3,
        }

        # Sum the weights
        add_results[0] = weight0 + weight2
        add_results[1] = bias0 + bias2
        add_results[2] = weight1 + weight3
        add_results[3] = bias1 + bias3

        address2 = config["ip"]
        # Save the weights
        for i in range(len(add_results)):
            with open(f"../mnist_model/weights/{address2}_torch_weights"+str(i)+".json", "w") as json_file:
                json.dump(add_results[i], json_file)

        # Send weights to next
        for i in range(4):
            file_path = "../mnist_model/weights/{address2}_torch_weights"+str(i)+".json"
            with open(file_path, "rb") as f:
                files = {"file" : (file_path, f.read())}
                request.post(f"http://address:5000/", files=files)

    return
