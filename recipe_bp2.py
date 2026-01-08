from flask import Blueprint

recipe_bp2 = Blueprint('recipe_bp2', __name__)

@recipe_bp2.route('/recipe2')
def recipe2():
    return "Recipe Register HTML - Not implemented"
