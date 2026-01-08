from flask import Blueprint

bc_basic = Blueprint('blockchain_basic', __name__)

@bc_basic.route('/bc_basic')
def bc_basic_page():
    return "Blockchain Basic - Not implemented"
