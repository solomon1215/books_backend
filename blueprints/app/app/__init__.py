from .app import app

from sanic import Blueprint

app = Blueprint.group(app, url_prefix='/app')