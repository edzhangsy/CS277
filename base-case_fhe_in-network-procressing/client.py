from flask import Blueprint, current_app, request
import requests
import subprocess
import tenseal
import ast

client_bp = Blueprint('client', __name__)

config = {}

context = None
switch_address = None
received_file_count = 0

def init(config):
    global switch_address

    switch_address = config["send"]

    return

@client_bp.route("/setup_context_t", methods=["POST"])
def setup_context():
    global context

    print("Client Setup Context")
    file = request.files["file"]
    file.save(f"{file.filename}")

    with open("./private_context.pkl", "rb") as f:
        context = tenseal.context_from(f.read())

    return ""


@client_bp.route("/train")
def train():
    global switch_address
    global config

    print("Client Train")
    command = ["python", "../mnist_model/mnist.py"]

    # Run the training
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing mnist_model.py: {e}")

    # Encrypt and serialize
    results = encrypt_and_serialize()
            
    # Send the weights to the switch
    address = config["ip"]
    for i in range(4):
        file_path = f"../mnist_model/weights/torch_weights{i}.pkl"
        with open(file_path, "wb") as f:
            f.write(results[i])

    for i in range(4):
        file_path = f"../mnist_model/weights/torch_weights{i}.pkl"
        with open(file_path, "rb") as f:
            print(f"Client send to: {switch_address}")
            file_path = "../mnist_model/weights/{address}_torch_weights{i}.pkl"
            files = {"file" : (file_path, f.read())}
            requests.post(f"http://{switch_address:5000/}", files=files)

    return ""


@client_bp.route("/continue_training", methods=["POST"])
def continue_traning():
    global received_file_count
    global config

    print("Client Continue Training")
    file = request.files["file"]
    file.save(f"{file.filename}")

    received_file_count += 1

    # Check if the client has received 4 files
    print(f"Client files received: {received_file_count}")
    if received_file_count == 4:
        received_file_count = 0

        # Deserialize and remove encryption
        remove_serialization_and_encryption()

        command = ["python", "../mnist_model/replace_weights_mnist.py"]

        try:
                subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
                print(f"Error executing replace_weights_mnist.py: {e}")

        # Encrypt and serialize
        results = encryption_and_serialization()

        for i in range(4):
            file_path = f"../mnist_model/weights/torch_weights{i}.pkl"
            with open(file_path, "wb") as f:
                f.write(results[i])

        # Send weights to the switch
        address = config["ip"]
        for i in range(4):
                file_path = f"../mnist_model/weights/torch_weights{i}.pkl"
                with open(file_path, "rb") as f:
                    print(f"Client send to: {switch_address}")
                    file_path = f"../mnist_model/weights/{address}_torch_weights{i}.pkl"
                    files = {"file" : (file_path, f.read())}
                    requests.post(f"http://{switch_address}:5000/", files=files)

    return ""

def encrypt_and_serialize():
    # Read weights
    weight0 = None
    bias0 = None
    weight1 = None
    bias1 = None

    for i in range(4):
        file_path = f"../mnist_model/weights/torch_weights{i}.json"
        with open(file_path, "rb") as f:
            if i == 0:
                weight0 = ast.literal_eval(f.read())
            elif i == 1:
                bias0 = ast.literal_eval(f.read())
            elif i == 2:
                weight1 = ast.literal_eval(f.read())
            elif i == 3:
                bias1 = ast.literal_eval(f.read())

    # Encrypt weights
    weight0_enc = tenseal.ckks_tensor(context, weight0)
    bias0_enc = tenseal.ckks_tensor(context, bias0)
    weight1_enc = tenseal.ckks_tensor(context, weight1)
    bias1_enc = tenseal.ckks_tensor(context, bias1)

    # Serialize weights
    results = {
        0: None,
        1: None,
        2: None,
        3: None
    }

    results[0] = weight0_enc.serialize()
    results[1] = bias0_enc.serialize()
    results[2] = weight1_enc.serialize()
    results[3] = bias1_enc.serialize()

    return results

def remove_serializtaion_and_encryption():
    # Read serialized files
    weights = {
        0: None,
        1: None,
        2: None,
        3: None
    }

    for i in range(4):
        file_path = f"../mnist_model/weights/torch_weights{i}.pkl"
        with open(file_path, "rb") as f:
            weights[i] = f.read()

    # Remove serialization
    weights_results = {
        0: None,
        1: None,
        2: None,
        3: None
    }

    weights_results[0] = tenseal.ckks_tensor_from(context, weights[0])
    weights_results[1] = tenseal.ckks_tensor_from(context, weights[1])
    weights_results[2] = tenseal.ckks_tensor_from(context, weights[2])
    weights_results[3] = tenseal.ckks_tensor_from(context, weights[3])

    # Remove encryption
    results = {
        0: None,
        1: None,
        2: None,
        3: None
    }

    results[0] = weights_results[0].decrypt()
    results[1] = weights_results[1].decrypt()
    results[2] = weights_results[2].decrypt()
    results[4] = weights_results[3].decrypt()

    # Save as json files
    for i in range(4):
        with open(f"../mnist_model/weights/torch_weights{i}.json", "w") as f:
            json.dump(results[i], f)

    return
