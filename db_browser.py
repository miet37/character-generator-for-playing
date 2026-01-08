from flask import Blueprint

bp = Blueprint('db_browser', __name__)

@bp.route('/dbbrowser')
def dbbrowser():
    return "DB Browser - Not implemented"
