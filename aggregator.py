from flask import Blueprint, current_app

config = {}
log = {}

aggregator_bp = Blueprint('aggregator', __name__)

@aggregator_bp.route('/hello')
def hello():
    return 'hello from aggregator'
