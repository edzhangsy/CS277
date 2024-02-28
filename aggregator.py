from flask import Blueprint, current_app

aggregator_bp = Blueprint('aggregator', __name__)

config = {}
log = {}

@aggregator_bp.route('/a/hello')
def hello():
    return 'hello from aggregator'
