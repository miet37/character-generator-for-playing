from flask import Blueprint

bp = Blueprint('data_browser2', __name__)

@bp.route('/data_browser')
def data_browser():
    return "Data Browser - Not implemented"
