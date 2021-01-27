from service.base_service import BaseService
from model.user_model import UserLoginModel
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

import config


class UserService(BaseService):
    model_class = UserLoginModel

    @classmethod
    def get_user_auth(cls, username: str, password: str, **kwargs) -> bool:

        if username == config.ENV_LOGIN and password == config.ENV_PASSWORD:
            return True
        try:
            user = cls.get(hash_key=username)
            user_password_hash = user.password
            return user_password_hash == cls.get_password_hash(password)
        except cls.model_class.DoesNotExist:
            return False

    @classmethod
    def get_token(cls, username: str) -> str:
        access_token = create_access_token(identity=username)
        return access_token

    @classmethod
    def get_password_hash(cls, plain_password: str) -> str:
        return generate_password_hash(plain_password)
