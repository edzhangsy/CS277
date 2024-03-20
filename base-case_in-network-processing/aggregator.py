from flask import Blueprint, current_app, request
from multiprocessing import Pool
import ast
import requests
import json

aggregator_bp = Blueprint('aggregator', __name__)

config = {}
log = {}
#context = None
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
    if received_file_count == 8:
        received_file_count = 0
        sender_address = sender_addr()
        address1 = sender_address[0]
        address2 = sender_address[1]
        for i in range(4):
            with open(f"../mnist_model/weights/{address1}_torch_weights"+str(i)+".json", "r") as json_file:
                if i == 0:
                    weight0 = ast.literal_eval(json_file.read())
                elif i == 1:
                    bias0 = ast.literal_eval(json_file.read())
                elif i == 2:
                    weight1 = ast.literal_eval(json_file.read())
                elif i == 3:
                    bias1 = ast.literal_eval(json_file.read())

        for i in range(4):
            with open(f"../mnist_model/weights/{address2}_torch_weights"+str(i)+".json", "r") as json_file:
                if i == 0:
                    weight2 = ast.literal_eval(json_file.read())
                elif i == 1:
                    bias2 = ast.literal_eval(json_file.read())
                elif i == 2:
                    weight3 = ast.literal_eval(json_file.read())
                elif i == 3:
                    bias3 = ast.literal_eval(json_file.read())

        aggregation_results = {
                0: None,
                1: None,
                2: None,
                3: None,
                }

        num = num_clients()

        # Get the average
        #aggregation_results[0] = weight0 + weight2
        #aggregation_results[0] = [[element / num for element in sublist] for sublist in aggregation_results[0]]

        #aggregation_results[1] = bias0 + bias2
        #aggregation_results[1] = [element / num for element in aggregation_results[1]]

        #aggregation_results[2] = weight1 + weight3
        #aggregation_results[2] = [[element / num for element in sublist] for sublist in aggregation_results[2]]

        #aggregation_results[3] = bias1 + bias3
        #aggregation_results[3] = [element / num for element in aggregation_results[3]]

        aggregation_results[0] = [[element1 + element2 for element1, element2 in zip(sublist1, sublist2)] for sublist1, sublist2 in zip(weight0, weight2)]
        aggregation_results[0] = [[element / num for element in sublist] for sublist in aggregation_results[0]]

        aggregation_results[1] = [element1 + element2 for element1, element2 in zip(bias0, bias2)]
        aggregation_results[1] = [element / num for element in aggregation_results[1]]

        aggregation_results[2] = [[element1 + element2 for element1, element2 in zip(sublist1, sublist2)] for sublist1, sublist2 in zip(weight1, weight3)]
        aggregation_results[2] = [[element / num for element in sublist] for sublist in aggregation_results[2]]

        aggregation_results[3] = [element1 + element2 for element1, element2 in zip(bias1, bias3)]
        aggregation_results[3] = [element / num for element in aggregation_results[3]]

        # Save results
        for i in range(len(aggregation_results)):
            with open("../mnist_model/weights/torch_weights"+str(i)+".json", "w") as json_file:
                json.dump(aggregation_results[i], json_file)

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