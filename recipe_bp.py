from flask import Blueprint

recipe_bp = Blueprint('recipe_bp', __name__)

@recipe_bp.route('/recipe')
def recipe():
    return "Recipe Register JS - Not implemented"
