from flask import Blueprint

bc_fg_bp = Blueprint('blockchain_fgindex', __name__)

@bc_fg_bp.route('/fgindex')
def fgindex():
    return "FG Index - Not implemented"
