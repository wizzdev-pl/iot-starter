from http import HTTPStatus

import flask
import flask_restx

from core.utils import scan_with_pagination
from core.request_arguments_parser import core_request_arguments_parser
from core.response_factory import create_success_response, create_success_plain_response
from serializers.device_serializer import DeviceTypeSerializer
from service.device_service import DeviceTypeService
from flask_jwt_extended import jwt_required

device_type_schema = DeviceTypeSerializer()
device_type_namespace = flask_restx.Namespace("DeviceType")
device_type_namespace.add_model(device_type_schema.api_model.name, device_type_schema.api_model)


@device_type_namespace.route('/')
class DeviceTypeAllApi(flask_restx.Resource):

    @device_type_namespace.expect(core_request_arguments_parser)
    @device_type_namespace.response(HTTPStatus.OK.real, "List of device types", [device_type_schema.api_model])
    def get(self):
        """ Returns list of device types """
        device_types = scan_with_pagination(DeviceTypeService)
        return create_success_response(data=device_type_schema.serialize(device_types, many=True))

    @device_type_namespace.expect(device_type_schema.api_model)
    @device_type_namespace.response(HTTPStatus.CREATED.real,
                                    "Device type was successfully created",
                                    device_type_schema.api_model)
    @jwt_required()
    def post(self):
        """ Create new device """
        device_type_data = device_type_schema.loads_required(flask.request.data)
        device_type = DeviceTypeService.create_device_type(**device_type_data)
        return create_success_response(data=device_type_schema.serialize(device_type))


@device_type_namespace.route('/<hash_key>')
class DeviceTypeSelectedApi(flask_restx.Resource):

    @device_type_namespace.response(HTTPStatus.OK.real, "Selected device type", device_type_schema.api_model)
    def get(self, hash_key: str):
        """ Returns selected device type """
        device_type = DeviceTypeService.get(hash_key)
        return create_success_response(data=device_type_schema.serialize(device_type))

    @device_type_namespace.response(HTTPStatus.NO_CONTENT.real, "Device type was successfully removed")
    @jwt_required()
    def delete(self, hash_key: str):
        """ Remove selected device type """
        device_type = DeviceTypeService.get(hash_key)
        device_type.safe_delete()
        return create_success_plain_response(status_text=f"Device {hash_key} removed")

    @device_type_namespace.expect(device_type_schema.api_model)
    @device_type_namespace.response(HTTPStatus.OK.real, "Edited device type", device_type_schema.api_model)
    @jwt_required()
    def put(self, hash_key: str):
        """ Edit selected device type """
        device_type_data = device_type_schema.loads_required(flask.request.data)
        device_type = DeviceTypeService.put(**device_type_data)
        return create_success_response(data=device_type_schema.serialize(device_type))
