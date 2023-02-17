from http import HTTPStatus

import flask
import flask_restx

from core.utils import scan_with_pagination
from core.request_arguments_parser import core_request_arguments_parser
from core.response_factory import create_success_response, create_success_plain_response
from serializers.device_serializer import DeviceGroupSerializer
from service.device_service import DeviceGroupService
from flask_jwt_extended import jwt_required

device_group_schema = DeviceGroupSerializer()
device_group_namespace = flask_restx.Namespace("DeviceGroup")
device_group_namespace.add_model(device_group_schema.api_model.name, device_group_schema.api_model)


@device_group_namespace.route('/')
class DeviceGroupAllApi(flask_restx.Resource):

    @device_group_namespace.expect(core_request_arguments_parser)
    @device_group_namespace.response(HTTPStatus.OK.real, "List of device groups", [device_group_schema.api_model])
    def get(self):
        """ Returns list of device groups """
        device_groups = scan_with_pagination(DeviceGroupService)
        return create_success_response(data=device_group_schema.serialize(device_groups, many=True))

    @device_group_namespace.expect(device_group_schema.api_model)
    @device_group_namespace.response(HTTPStatus.CREATED.real,
                                     "Device group was successfully created",
                                     device_group_schema.api_model)
    @jwt_required()
    def post(self):
        """ Create new device """
        device_group_data = device_group_schema.loads_required(flask.request.data)
        device_group = DeviceGroupService.create_device_group(**device_group_data)
        return create_success_response(data=device_group_schema.serialize(device_group))


@device_group_namespace.route('/<hash_key>')
class DeviceGroupSelectedApi(flask_restx.Resource):

    @device_group_namespace.response(HTTPStatus.OK.real, "Selected device group", device_group_schema.api_model)
    def get(self, hash_key: str):
        """ Returns selected device group """
        device_group = DeviceGroupService.get(hash_key)
        return create_success_response(data=device_group_schema.serialize(device_group))

    @device_group_namespace.response(HTTPStatus.NO_CONTENT.real, "Device group was successfully removed")
    @jwt_required()
    def delete(self, hash_key: str):
        """ Remove selected device group """
        device_group = DeviceGroupService.get(hash_key)
        device_group.safe_delete()
        return create_success_plain_response(status_text=f"Device {hash_key} removed")

    @device_group_namespace.expect(device_group_schema.api_model)
    @device_group_namespace.response(HTTPStatus.OK.real, "Edited device group", device_group_schema.api_model)
    @jwt_required()
    def put(self, hash_key: str):
        """ Edit selected device group """
        device_group_data = device_group_schema.loads_required(flask.request.data)
        device_group = DeviceGroupService.put(**device_group_data)
        return create_success_response(data=device_group_schema.serialize(device_group))
