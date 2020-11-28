from sanic import Blueprint

from .api import api
from .app import app

bp = Blueprint.group(api, app)
