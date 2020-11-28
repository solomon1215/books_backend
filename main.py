#!/usr/bin/env python3

import logging
from sentry_sdk.integrations.sanic import SanicIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sanic import Sanic
from sanic_openapi import swagger_blueprint
from sanic_jwt import Initialize
from kirin.models.auth import *
# from kirin.celery.celery import celery_start, celery_stop
from config.settings import settings

from blueprints import bp


logging.basicConfig(filename='./logs/server.log', level=logging.INFO, format='%(asctime)s - [%(levelname)s] - (%(name)s): %(message)s')

app = Sanic(name="91T B2B API")
app.config.update(settings)

app.static('/static', './static')
app.static('/robots.txt', './robots.txt')
app.static('/favicon.ico', './static/icons/favicon.png')

app.blueprint(swagger_blueprint)
app.blueprint(bp)

Initialize(app, url_prefix='/user/auth',
           authenticate=authenticate,
           extend_payload=extend_payload,
           refresh_token_enabled=True,
           store_refresh_token=store_refresh_token,
           retrieve_user=retrieve_user,
           retrieve_refresh_token=retrieve_refresh_token,
           secret=settings['SANIC_JWT_SECRET'],
           claim_iat=True,
           claim_iss='API.B2B.91T.COM')

# app.register_listener(celery_stop, 'before_server_stop')


if __name__ == "__main__":
    # celery_start(app)
    app.run(host="0.0.0.0", port=8081, debug=True)
