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

@switch_bp.route("/setup_context", methods=["Post"])
def setup_context():
    global context

    print("Switch Setup Context")
    file = request.files["file"]
    file.save(f"{file.filename}")

    with open("./public_context.pkl", "rb") as f:
        context = tenseal.context_from(f.read())

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

    # Send weights to next
    with open(file.filename, "rb") as f:
        print(f"Switch send: {file.filename} to: {address}")
        files = {"file" : (file.filename, f.read())}
        requests.post(f"http://{address}:5000/", files=files)

    return ""
