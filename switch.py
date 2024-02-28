from flask import Blueprint, current_app

switch_bp = Blueprint('switch', __name__)

log = {}
config = {}

@switch_bp.route('/hello')
def hello():
    return 'Hello, from the switch'

def init(config):
    # do init here
    print(config)
