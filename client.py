from flask import Blueprint, current_app

client_bp = Blueprint('client', __name__)

log = {
    "iteration": [
        {
            "start_time": "timestamp",
            "end_time": "timestamp",
            "byte_received": 50,
            "byte_send": 100
        },
        {
            "start_time": "timestamp",
            "end_time": "timestamp",
            "byte_received": 50,
            "byte_send": 100
        },
        {
            "start_time": "timestamp",
            "end_time": "timestamp",
            "byte_received": 50,
            "byte_send": 100
        }
    ]
}
config = {}

@client_bp.route('/c/hello')
def hello():
    # Access the global value
    return 'hello from the client'

def init(config):
    # do init here
    print(config)

@client_bp.route('/c/receive')
def receive():
    pass
