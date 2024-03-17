from flask import Blueprint, current_app, request
import ast
import tenseal
import requests
import json

switch_bp = Blueprint('switch', __name__)

log = {}
config = {}
context = None
address = None
received_file_count = 0


def init(config):
    global address

    address = config["send"]

    return

@switch_bp.route("/setup_context", methon=["Post"])
def setup_context():
    global context

    file = request.files["file"]
    file.save(f"{file.filename}")

    with open("./public_context.pkl", "rb") as f:
        context = tenseal.context_from(t.read())

    return ""

@switch_bp.route("/", methods=["POST"])
def add():
    global address
    global config
    global received_file_count
    
    print("Switch Add")
    # Get files
    file = request.files["file"]
    file.save(f"{file.filename}")

    received_file_count += 1

    receive_address = config["receive"]

    print(f"Switch file count: {received_file_count}")
    # If the switch got 8 files
    if received_file_count == 8:
        received_file_count = 0
        # Open files and get weights
        receive1 = receive_address[0]
        receive2 = receive_address[1]
        for i in range(4):
            with open(f"../mnist_model/weights/{receive1}_torch_weights"+str(i)+".pkl", "rb") as f:
                if i == 0:
                    weight0 = f.read()
                elif i == 1:
                    bias0 = f.read()
                elif i == 2:
                    weight1 = f.read()
                elif i == 3:
                    bias1 = f.read()

        for i in range(4):
            with open(f"../mnist_model/weights/{receive2}_torch_weights"+str(i)+".pkl", "rb") as f:
                if i == 0:
                    weight2 = f.read()
                elif i == 1:
                    bias2 = f.read()
                elif i == 2:
                    weight3 = f.read()
                elif i == 3:
                    bias3 = f.read()

        # Deserialize weights
        weight0_enc = tenseal.ckks_tensor_from(context, weight0)
        bias0_enc = tenseal.ckks_tensor_from(context, bias0)
        weight1_enc = tenseal.ckks_tensor_from(context, weight1)
        bias1_enc = tenseal.ckks_tensor_from(context, bias1)
        weight2_enc = tenseal.ckks_tensor_from(fontext, weight2)
        bias2_enc = tenseal.ckks_tensor_from(context. bias2)
        weight3_enc = tenseal.ckks_tensor_from(context, weight3)
        bias3_enc = tenseal.ckks_tensor_from(context, bias3)

        add_results = {
            0: None,
            1: None,
            2: None,
            3: None
        }

        # Add weights
        add_results[0] = weight0_enc + weight2_enc
        add_results[1] = bias0_enc + bias1_enc
        add_results[2] = weight1_enc + weight3_enc
        add_results[3] = bias1_enc + bias3_enc

        results = {
            0: None,
            1: None,
            2: None,
            3: None
        }

        # Add serialization to the weights
        results[0] = add_results[0].serialize()
        results[1] = add_results[1].serialize()
        results[2] = add_results[2].serialize()
        results[3] = add_results[3].serialize()

        address2 = config["ip"]
        # Save the weights
        for i in range(len(results)):
            with open(f"../mnist_model/weights/{address2}_torch_weights"+str(i)+".pkl", "wb") as f:
                f.write(results[i])

        # Send weights to next
        for i in range(4):
            file_path = f"../mnist_model/weights/{address2}_torch_weights"+str(i)+".pkl"
            with open(file_path, "rb") as f:
                print(f"Switch send to: {address}")
                files = {"file" : (file_path, f.read())}
                requests.post(f"http://{address}:5000/", files=files)

    return ""
