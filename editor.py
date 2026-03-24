from flask import Blueprint, render_template

editor_bp = Blueprint('editor', __name__)

@editor_bp.route('/')
def index():
    return render_template('traducteur.html')