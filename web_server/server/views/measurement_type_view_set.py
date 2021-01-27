from http import HTTPStatus

import flask
import flask_restx

from core.utils import scan_with_pagination
from core.request_arguments_parser import core_request_arguments_parser
from core.response_factory import create_success_response, create_success_plain_response
from serializers.measurement_serializer import MeasurementTypeSerializer
from service.measurement_service import MeasurementTypeService


measurement_type_schema = MeasurementTypeSerializer()
measurement_type_namespace = flask_restx.Namespace("MeasurementType")
measurement_type_namespace.add_model(measurement_type_schema.api_model.name, measurement_type_schema.api_model)


@measurement_type_namespace.route('/')
class MeasurementTypeAllApi(flask_restx.Resource):

    @measurement_type_namespace.expect(core_request_arguments_parser)
    @measurement_type_namespace.response(HTTPStatus.OK.real,
                                         "List of measurement types",
                                         [measurement_type_schema.api_model])
    def get(self):
        """ Returns list of measurement types """
        measurement_types = scan_with_pagination(MeasurementTypeService)
        return create_success_response(data=measurement_type_schema.serialize(measurement_types, many=True))

    @measurement_type_namespace.expect(measurement_type_schema.api_model)
    @measurement_type_namespace.response(HTTPStatus.CREATED.real,
                                         "Measurement type was successfully created",
                                         measurement_type_schema.api_model)
    def post(self):
        """ Create new measurement type """
        measurement_type_data = measurement_type_schema.loads_required(flask.request.data)
        measurement_type = MeasurementTypeService.create_measurement_type(**measurement_type_data)
        return create_success_response(data=measurement_type_schema.serialize(measurement_type))


@measurement_type_namespace.route('/<hash_key>')
class DeviceSelectedApi(flask_restx.Resource):

    @measurement_type_namespace.response(HTTPStatus.OK.real,
                                         "Selected measurement type", measurement_type_schema.api_model)
    def get(self, hash_key: str):
        """ Returns selected measurement type """
        measurement_type = MeasurementTypeService.get(hash_key)
        return create_success_response(data=measurement_type_schema.serialize(measurement_type))

    @measurement_type_namespace.response(HTTPStatus.NO_CONTENT.real, "Measurement type was successfully removed")
    def delete(self, hash_key: str):
        """ Remove selected measurement type """
        measurement_type = MeasurementTypeService.get(hash_key)
        measurement_type.safe_delete()
        return create_success_plain_response(status_text=f"Measurement type {hash_key} removed")

    @measurement_type_namespace.expect(measurement_type_schema.api_model)
    @measurement_type_namespace.response(HTTPStatus.OK.real,
                                         "Edited measurement type",
                                         measurement_type_schema.api_model)
    def put(self, hash_key: str):
        """ Edit selected measurement type """
        measurement_type_data = measurement_type_schema.loads_required(flask.request.data)
        measurement_type = MeasurementTypeService.put(**measurement_type_data)
        return create_success_response(data=measurement_type_schema.serialize(measurement_type))
