from flask import Blueprint, current_app, request
import requests
import subprocess

client_bp = Blueprint('client', __name__)

config = {}

#context = None
switch_address = None
numClients = None
clientIndex = None
received_file_count = 0

def init(config):
    #global context
    global switch_address
    global numClients
    global clientIndex

    #context = config["context"]
    switch_address = config["send"]
    numClients = config["client_number"]
    clientIndex = config["index"]

    return


@client_bp.route("/train")
def train():
    global switch_address
    global config
    global numClients
    global clientIndex

    print("Client Train")
    command = ["python", "../mnist_model/mnist.py", str(numClients), str(clientIndex)]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing mnist_model.py: {e}")

    # Encrypt and serialize

    address = config["ip"]
    for i in range(4):
        file_path = f"../mnist_model/weights/torch_weights{i}.json"
        with open(file_path, "rb") as f:
            file_path = f"../mnist_model/weights/{address}_torch_weights{i}.json"
            print(f"Sending: {file_path}")
            files = {"file" : (file_path, f.read())}
            response = requests.post(f"http://{switch_address}:5000/", files=files)

    return ""


@client_bp.route("/continue_training", methods=["POST"])
def continue_traning():
    global received_file_count
    global config
    global numClients
    global clientIndex

    print("Client Continue Training")
    file = request.files["file"]
    file.save(f"{file.filename}")

    received_file_count += 1

    print(f"Client files received: {received_file_count}")
    if received_file_count == 4:
        received_file_count = 0
        # Deserialize and remove encryption

        command = ["python", "../mnist_model/replace_weights_mnist.py", str(numClients), str(clientIndex)]

        try:
                subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
                print(f"Error executing replace_weights_mnist.py: {e}")

        # Encrypt and serialize

        address = config["ip"]
        for i in range(4):
            # Where does replace_weights_mnist save files?
            file_path = f"../mnist_model/weights/torch_weights{i}.json"
            with open(file_path, "rb") as f:
                print(f"Client send: {file_path} to: {switch_address}")
                file_path = f"../mnist_model/weights/{address}_torch_weights{i}.json"
                files = {"file" : (file_path, f.read())}
                requests.post(f"http://{switch_address}:5000/", files=files)

    return ""
