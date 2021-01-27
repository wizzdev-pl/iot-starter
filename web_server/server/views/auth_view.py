import flask_restx

from serializers.user_serializer import UserLoginSerializer
from core.user_service import UserService
from core.response_factory import *

login_schema = UserLoginSerializer()
auth_namespace = flask_restx.Namespace("Auth")
auth_namespace.add_model(login_schema.api_model.name, login_schema.api_model)

@auth_namespace.route('/login')
class UserLoginApi(flask_restx.Resource):

    @auth_namespace.expect(login_schema.api_model)
    @auth_namespace.response(HTTPStatus.CREATED.real, "You are successfully log in")
    def post(self):
        """Log in using username and password"""
        auth_data = login_schema.loads_required(flask.request.data)
        auth = UserService.get_user_auth(**auth_data)

        if auth:
            access_token = UserService.get_token(auth_data['username'])
            return create_success_response(data=access_token)
        else:
            return create_failed_response("Invalid username or password")
