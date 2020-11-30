#!/usr/bin/env python3

from sanic import Sanic
from sanic_openapi import swagger_blueprint
from sanic_jwt import Initialize
from kirin.models.auth import *
from config.settings import settings
from sanic_cors import CORS

from blueprints import bp


logging.basicConfig(filename='./logs/server.log', level=logging.INFO, format='%(asctime)s - [%(levelname)s] - (%(name)s): %(message)s')

app = Sanic(name="BOOKS BACKEND")
cors = CORS(app, resources={r"/api/admin/*": {"origins": "*"}})
app.config.update(settings)

app.static('/static', './static')
app.static('/robots.txt', './robots.txt')
app.static('/favicon.ico', './static/icons/favicon.png')

app.blueprint(swagger_blueprint)
app.blueprint(bp)

Initialize(app, url_prefix='/api/admin/users/auth',
           authenticate=authenticate,
           extend_payload=extend_payload,
           refresh_token_enabled=True,
           store_refresh_token=store_refresh_token,
           retrieve_user=retrieve_user,
           retrieve_refresh_token=retrieve_refresh_token,
           secret=settings['SANIC_JWT_SECRET'],
           claim_iat=True,
           expiration_delta=60*24*7,
           claim_iss='BOOKS BACKEND')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, workers=8, auto_reload=True, access_log=True, debug=False)
