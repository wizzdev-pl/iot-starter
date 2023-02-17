import http
import os

import sentry_sdk
import flask
import flask_restx
import flask_lambda
import marshmallow
import pynamodb.exceptions
from flask_jwt_extended import JWTManager

import core.response_factory
import config
import common.errors
import views.device_view_set
import views.device_group_view_set
import views.device_type_view_set
import views.measurement_type_view_set
import views.measurement_view_set
import views.auth_view

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
}
app = flask_lambda.FlaskLambda(__name__)
api = flask_restx.Api(app, version='1.0', title="Wizzdev IoT API", prefix="/api", doc="/api/", security='Bearer Auth',
                      authorizations=authorizations)

api.add_namespace(views.device_view_set.device_namespace)
api.add_namespace(views.device_type_view_set.device_type_namespace)
api.add_namespace(views.device_group_view_set.device_group_namespace)
api.add_namespace(views.measurement_type_view_set.measurement_type_namespace)
api.add_namespace(views.measurement_view_set.measurement_namespace)
api.add_namespace(views.auth_view.auth_namespace)

app.config['JWT_SECRET_KEY'] = config.SECRET_KEY
jwt = JWTManager(app)

sentry_dsn = os.environ.get('SENTRY')
if sentry_dsn:
    sentry_sdk.init(sentry_dsn, environment=os.environ.get("MODE", "undefined"))


@jwt.additional_claims_loader
def add_claims_to_access_token(access_level):
    return {'access_level': access_level}


@app.errorhandler(marshmallow.ValidationError)
def handle_payload_validation_error(error):
    return core.response_factory.create_invalid_request_data_response(status_text=str(error))


@app.errorhandler(common.errors.ItemDoesNotExist)
@app.errorhandler(pynamodb.exceptions.DoesNotExist)
def handle_item_does_not_exist_error(error):
    return core.response_factory.create_not_found_response()


@app.errorhandler(Exception)
def handle_all_exceptions(error):
    return core.response_factory.create_failed_response(status_text=str(error))


@app.after_request
def add_no_robots_html_header(response: flask.Response):
    if config.NO_ROBOTS:
        response.headers['X-Robots-Tag'] = "noindex, nofollow, noarchive"
    if config.CORS:
        response.headers['Access-Control-Allow-Origin'] = "*"
    return response


@app.route('/')
def get_website() -> flask.Response:
    return flask.send_file(os.path.join("client", "index.html"))


@app.route('/js/<path:path>')
def get_js_resource(path) -> flask.Response:
    return flask.send_file(os.path.join('client', 'js', path))


@app.route('/css/<path:path>')
def get_css_resource(path) -> flask.Response:
    return flask.send_file(os.path.join('client', 'css', path))


@app.route('/favicon.ico')
def get_favicon():
    return flask.send_file(os.path.join("client", "favicon.png"))


@app.route('/#<path:path>')
def redirect_front(path=None):
    return flask.redirect("/")
