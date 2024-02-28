from flask import Blueprint, current_app

client_bp = Blueprint('client', __name__)

log = {}
config = {}

@client_bp.route('/hello')
def hello():
    # Access the global value
    return 'hello from the client'

def init(config):
    # do init here
    print(config)
