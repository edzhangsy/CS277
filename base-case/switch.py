from flask import Blueprint, current_app, request
import ast
#import tenseal
import requests
import json

switch_bp = Blueprint('switch', __name__)

log = {}
config = {}
address = None

def init(config):
    global address

    address = config["send"]

    return

@switch_bp.route("/", methods=["POST"])
def add():
    global address
    global config
    
    # Get files
    file = request.files["file"]

    # Send to next
    for i in range(4):
        with open(file_path, "rb") as f:
            print(f"Switch send to: {address}")
            files = {"file" : file}
            requests.post(f"http://{address}:5000/", files=files)

    return ""
