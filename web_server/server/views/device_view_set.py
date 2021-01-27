import random
import logging
import json

import flask_restx
import boto3
import botocore.exceptions

from core.things_helper import create_thing, get_thing_certificates
from core.utils import scan_with_pagination
from core.response_factory import *
from core.request_arguments_parser import core_request_arguments_parser
from serializers.device_serializer import DeviceSerializer
from service.device_service import DeviceService
from flask_jwt_extended import jwt_required

device_schema = DeviceSerializer()
device_namespace = flask_restx.Namespace("Device")
device_namespace.add_model(device_schema.api_model.name, device_schema.api_model)

device_shadow_parser = flask_restx.reqparse.RequestParser()
device_shadow_parser.add_argument('region', help="The AWS zone, default is eu-west-2", type=str)


@device_namespace.route('/')
class DeviceAllApi(flask_restx.Resource):

    @device_namespace.expect(core_request_arguments_parser)
    @device_namespace.response(HTTPStatus.OK.real, "List of devices", [device_schema.api_model])
    def get(self):
        """ Returns list of devices """
        devices = scan_with_pagination(DeviceService)
        return create_success_response(data=device_schema.serialize(devices, many=True))

    @device_namespace.expect(device_schema.api_model)
    @device_namespace.response(HTTPStatus.CREATED.real, "Device and thing was successfully created", device_schema.api_model)
    @jwt_required
    def post(self):
        """ Create new device and new thing """
        device_data = device_schema.loads_required(flask.request.data)
        create_thing(device_data)
        thing_certificates = get_thing_certificates(device_data['device_id'])

        device = DeviceService.create_device(**device_data)
        device_data = device_schema.serialize(device)

        data = dict(device_data, **thing_certificates)
        return create_success_response(data=data)


@device_namespace.route('/<hash_key>')
class DeviceSelectedApi(flask_restx.Resource):

    @device_namespace.response(HTTPStatus.OK.real, "Selected device", device_schema.api_model)
    def get(self, hash_key: str):
        """ Returns selected device """
        device = DeviceService.get(hash_key)
        return create_success_response(data=device_schema.serialize(device))

    @device_namespace.response(HTTPStatus.NO_CONTENT.real, "Device was successfully removed")
    @jwt_required
    def delete(self, hash_key: str):
        """ Remove selected device """
        device = DeviceService.get(hash_key)
        device.safe_delete()
        return create_success_plain_response(status_text=f"Device {hash_key} removed")

    @device_namespace.expect(device_schema.api_model)
    @device_namespace.response(HTTPStatus.NO_CONTENT.real, "Device was successfully edited")
    @jwt_required
    def put(self, hash_key: str):
        """ Edit selected device """
        device_data = device_schema.loads_required(flask.request.data)
        device = DeviceService.put(**device_data)
        return create_success_response(data=device_schema.serialize(device))


@device_namespace.route("/<hash_key>/shadow")
class DeviceSelectedShadowApi(flask_restx.Resource):

    @staticmethod
    def secure_confidential_information(data: dict):
        if 'config' in data:
            config = data['config']
            if 'aws_endpoint' in config:
                data['config']['aws_endpoint'] = "*" * random.randint(5, 10)
            if 'password' in config:
                data['config']['password'] = "*" * random.randint(5, 10)
        return data

    @device_namespace.expect(device_shadow_parser)
    @device_namespace.response(HTTPStatus.OK.real, "Selected device shadow")
    @jwt_required
    def get(self, hash_key: str):
        """ Get classic shadow for selected device """
        try:
            region = device_shadow_parser.parse_args().get('region', 'eu-west-2')
            iot_core = boto3.client('iot-data', region_name=region)
            shadow_object = iot_core.get_thing_shadow(thingName=hash_key)
            shadow_object = shadow_object['payload'].read()
            shadow_object = json.loads(shadow_object)
            shadow_object_state = shadow_object.get('state', {})
            shadow_object_state_reported = shadow_object_state.get('reported', {})
            shadow_object_state_reported_secure = self.secure_confidential_information(shadow_object_state_reported)
            return create_success_response(data=shadow_object_state_reported_secure)
        except botocore.exceptions.ClientError:
            logging.exception("Cannot find shadow")
            return create_not_found_response()
        except json.JSONDecodeError:
            logging.exception("Cannot read shadow")
            return create_failed_response(f"Cannot read shadow for device {hash_key}")
