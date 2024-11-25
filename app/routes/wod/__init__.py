from flask import Blueprint

wod_bp = Blueprint('wod_bp', __name__, url_prefix='/wod')

from . import routes
