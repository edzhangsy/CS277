from flask import Blueprint, current_app, request
from multiprocessing import Pool
import ast
import requests
import json
import tenseal

aggregator_bp = Blueprint('aggregator', __name__)

config = {}
log = {}
context = None
iterations = 0
received_file_count = 0
pool = Pool(16)

@aggregator_bp.route("/train")
def train():
    global config
    global pool

    print("Aggregator Train")
    for key, value in config["others"].items():
        t = value["type"]
        if value["type"] == "client":
            print(f"training: {key}, type {t}")
            #requests.get(f"http://{key}:5000/train")
            pool.apply_async(requests.get, (f"http://{key}:5000/train",))
    return "training"

@aggregator_bp.route("/", methods=["POST"])
def aggregate():
    global received_file_count
    global iterations
    global config
    global pool

    print("Aggregator Continue Training")
    # Get files and save
    file = request.files["file"]
    file.save(f"{file.filename}")

    received_file_count += 1

    print(f"Aggregator file count: {received_file_count}")
    # Get the weights
    if received_file_count == (num_clients() * 4):
        received_file_count = 0

        address = clients_address()
        weights = {}
        k = 0

        for i in range(len(address)):
            for j in range(4):
                with open(f"../mnist_model/weights/{address[i]}_torch_weights"+str(j)+".pkl", "rb") as pkl:
                    weights[k] = pkl.read()
                    k += 1

        weights_enc = {}

        # Remove serialization
        for i in range(len(weights)):
            weights_enc[i] = tenseal.ckks_tensor_from(context, weights[i])

        aggregation_results = {
                0: None,
                1: None,
                2: None,
                3: None,
                }

        num = 1 / num_clients()

        # Average weights
        aggregation_results[0] = weights_enc[0]
        aggregation_results[1] = weights_enc[1]
        aggregation_results[2] = weights_enc[2]
        aggregation_results[3] = weights_enc[3]

        for i in range(4, len(weights_enc), 4):
            aggregation_results[0] = aggregation_results[0] + weights_enc[i]
        aggregation_results[0] = aggregation_results[0] * num

        for i in range(5, len(weights_enc), 4):
            aggregation_results[1] = aggregation_results[1] + weights_enc[i]
        aggregation_results[1] = aggregation_results[1] * num

        for i in range(6, len(weights_enc), 4):
            aggregation_results[2] = aggregation_results[2] + weights_enc[i]
        aggregation_results[2] = aggregation_results[2] * num

        for i in range(7, len(weights_enc), 4):
            aggregation_results[3] = aggregation_results[3] + weights_enc[i]
        aggregation_results[3] = aggregation_results[3] * num

        results = {
            0: None,
            1: None,
            2: None,
            3: None
        }

        # Serialize weights
        #results_ser[0] = aggregation_results[0].serialize()
        #results_ser[1] = aggregation_results[1].serialize()
        #results_ser[2] = aggregation_results[2].serialize()
        #results_ser[3] = aggregation_results[3].serialize()

        # Save results
        #for i in range(len(results_ser)):
        #    with open("../mnist_model/weights/torch_weights"+str(i)+".pkl", "wb") as f:
        #        f.write(results_ser[i])

        # Decrypt
        results[0] = aggregation_results[0].decrypt(context.secret_key()).tolist()
        results[1] = aggregation_results[1].decrypt(context.secret_key()).tolist()
        results[2] = aggregation_results[2].decrypt(context.secret_key()).tolist()
        results[3] = aggregation_results[3].decrypt(context.secret_key()).tolist()

        # Save as json
        for i in range(4):
            with open(f"../mnist_model/weights/torch_weights{i}.json", "w") as f:
                json.dump(results[i], f)

        clients = clients_address()

        print(f"iterations: {iterations}")
        # Send the results
        if iterations > 0:
            iterations -= 1
            for i in range(len(clients)):
                for j in range(4):
                    file_path = "../mnist_model/weights/torch_weights"+str(j)+".json"
                    with open(file_path, "rb") as f:
                        print(f"Aggregate sending to: {clients[i]}")
                        files = {"file" : (file_path, f.read())}
                        pool.apply_async(requests.post, (f"http://{clients[i]}:5000/continue_training",), kwds={"files": files})
                        #requests.post(f"http://{clients[i]}:5000/continue_training", files=files)

    print("Aggregator return")
    return ""


def num_clients():
    global config

    count = 0

    for key, value in config["others"].items():
        if value["type"] == "client":
            count += 1

    return count

def clients_address():
    global config

    clients = []

    for key, value in config["others"].items():
        if value["type"] == "client":
            clients.append(key)

    return clients

def sender_addr():
    global config

    address = []

    for key, value in config["others"].items():
        if value["send"] == "10.10.1.1":
            address.append(key)

    return address

def requests_post(address, files):

    requests.post(address, files=files)

    return
