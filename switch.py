from flask import Blueprint, current_app

switch_bp = Blueprint('switch', __name__)

log = {}
config = {}

@switch_bp.route('/s/hello')
def hello():
    return 'Hello, from the switch'

def init(config):
    print(log)
    # do init here
    print(config)


@switch_bp.route('/s/receive')
def receive():
    pass
