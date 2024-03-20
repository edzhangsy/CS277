from flask import Blueprint, current_app, request
from multiprocessing import Pool
import ast
import requests
import json
import logging
import os

aggregator_bp = Blueprint('aggregator', __name__)

config = {}
log = {}
logger = logging.getLogger(__name__)
logging.basicConfig(filename='output.log', filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)
#context = None
iterations = 0
round = 1
totalData = 0
received_file_count = 0
pool = Pool(16)

@aggregator_bp.route("/train")
def train():
    global config
    global pool

    print("Aggregator Train")
    logger.info("Training has begun")
    logger.info("Round 1 has begun")
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
    global round
    global totalData

    print("Aggregator Continue Training")
    # Get files and save
    file = request.files["file"]
    print(f"Saving: {file.filename}")
    file.save(f"{file.filename}")

    received_file_count += 1

    file_name = file.filename
    file_size = (os.stat(file_name)).st_size
    totalData += file_size
    logger.info('file of size %d received', file_size)

    print(f"Aggregator file count: {received_file_count}")
    # Get the weights
    if received_file_count == (num_clients() * 4):
        logger.info('Round %d completed!', round)
        round += 1
        logger.info('Round %d has begun', round)
        received_file_count = 0
        address = clients_address()

        weights = {}
        k = 0

        for i in range(len(address)):
            for j in range(4):
                with open(f"../mnist_model/weights/{address[i]}_torch_weights"+str(j)+".json", "r") as json_file:
                    weights[k] = ast.literal_eval(json_file.read())
                    k += 1

        aggregation_results = {
                0: None,
                1: None,
                2: None,
                3: None
                }

        num = num_clients()

        aggregation_results[0] = weights[0]
        aggregation_results[1] = weights[1]
        aggregation_results[2] = weights[2]
        aggregation_results[3] = weights[3]

        for i in range(4, len(weights), 4):
            aggregation_results[0] = [[element1 + element2 for element1, element2 in zip(sublist1, sublist2)] for sublist1, sublist2 in zip(aggregation_results[0], weights[i])]
        aggregation_results[0] = [[element / num for element in sublist] for sublist in aggregation_results[0]]

        for i in range(5, len(weights), 4):
            aggregation_results[1] = [element1 + element2 for element1, element2 in zip(aggregation_results[1], weights[i])]
        aggregation_results[1] = [element / num for element in aggregation_results[1]]

        for i in range(6, len(weights), 4):
            aggregation_results[2] = [[element1 + element2 for element1, element2 in zip(sublist1, sublist2)] for sublist1, sublist2 in zip(aggregation_results[2], weights[i])]
        aggregation_results[2] = [[element / num for element in sublist] for sublist in aggregation_results[2]]

        for i in range(7, len(weights), 4):
            aggregation_results[3] = [element1 + element2 for element1, element2 in zip(aggregation_results[3], weights[i])]
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

                        file_name = files.filename
                        file_size = (os.stat(file_name)).st_size
                        totalData += file_size
                        logger.info('file of size %d transmitted', file_size)

                        pool.apply_async(requests.post, (f"http://{clients[i]}:5000/continue_training",), kwds={"files": files})
                        #requests.post(f"http://{clients[i]}:5000/continue_training", files=files)
        else:
            logger.info('Total data sent in bytes is %d', totalData)
            logger.info("Training has ended")

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
