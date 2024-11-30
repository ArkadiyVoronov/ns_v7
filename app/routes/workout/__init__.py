from flask import Blueprint

workout_bp = Blueprint('workout_bp', __name__, url_prefix='/workout')

from . import routes
