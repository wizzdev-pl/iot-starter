from http import HTTPStatus
import time

import flask
import flask_restx

from core.response_factory import create_success_response, create_success_plain_response
from serializers.measurement_serializer import MeasurementSerializer
from service.measurement_service import MeasurementService

FOUR_HOURS_IN_SECONDS = 60 * 60 * 4

measurement_schema = MeasurementSerializer()
measurement_namespace = flask_restx.Namespace("Measurement")
measurement_namespace.add_model(measurement_schema.api_model.name, measurement_schema.api_model)

measurement_timestamp_parser = flask_restx.reqparse.RequestParser()
measurement_timestamp_parser.add_argument('minTimestamp', help="Minimum Read Datetime Default is last 4 hours. ", type=float)
measurement_timestamp_parser.add_argument('maxTimestamp', help="Maximum Read Datetime. Default is now. ", type=float)


@measurement_namespace.route('/')
class MeasurementAllApi(flask_restx.Resource):

    @measurement_namespace.expect(measurement_timestamp_parser)
    @measurement_namespace.response(HTTPStatus.OK.real, "List of measurement", [measurement_schema.api_model])
    def get(self):
        """ Returns list of measurement types """
        MeasurementModel = MeasurementService.model_class
        measurement_timestamp_options = measurement_timestamp_parser.parse_args()
        min_timestamp = measurement_timestamp_options.minTimestamp or time.time() * 1000 - FOUR_HOURS_IN_SECONDS
        max_timestamp = measurement_timestamp_options.maxTimestamp or time.time() * 1000
        measurements = MeasurementService.scan(filter_condition=(MeasurementModel.timestamp > min_timestamp) & (MeasurementModel.timestamp < max_timestamp))
        return create_success_response(data=measurement_schema.serialize(measurements, many=True))

    @measurement_namespace.expect(measurement_schema.api_model)
    @measurement_namespace.response(HTTPStatus.CREATED.real,
                                    "Measurement was successfully created",
                                    measurement_schema.api_model)
    def post(self):
        """ Create new measurement """
        measurement_data = measurement_schema.loads_required(flask.request.data)
        measurement = MeasurementService.create_measurement(**measurement_data)
        return create_success_response(data=measurement_schema.serialize(measurement))


@measurement_namespace.route('/<hash_key>/')
class DeviceMeasurementAllApi(flask_restx.Resource):

    @measurement_namespace.expect(measurement_timestamp_parser)
    @measurement_namespace.response(HTTPStatus.OK.real, "List of measurement", [measurement_schema.api_model])
    def get(self, hash_key: str):
        """ Returns measurement of selected device """
        MeasurementModel = MeasurementService.model_class
        measurement_timestamp_options = measurement_timestamp_parser.parse_args()
        min_timestamp = measurement_timestamp_options.minTimestamp or time.time() * 1000 - FOUR_HOURS_IN_SECONDS
        max_timestamp = measurement_timestamp_options.maxTimestamp or time.time() * 1000
        measurements = MeasurementService.scan(filter_condition=((MeasurementModel.device_id == hash_key) &
                                               (MeasurementModel.timestamp > min_timestamp) &
                                               (MeasurementModel.timestamp < max_timestamp))) # TODO: Change to query
        return create_success_response(data=measurement_schema.serialize(measurements, many=True))


@measurement_namespace.route('/<hash_key>/<range_key>')
class MeasurementSelectedApi(flask_restx.Resource):

    @measurement_namespace.response(HTTPStatus.OK.real, "Selected measurement", measurement_schema.api_model)
    def get(self, hash_key: str, range_key: str):
        """ Returns selected measurement """
        measurement = MeasurementService.get(hash_key, range_key)
        return create_success_response(data=measurement_schema.serialize(measurement))

    @measurement_namespace.response(HTTPStatus.NO_CONTENT.real, "Measurement was successfully removed")
    def delete(self, hash_key: str):
        """ Remove selected measurement """
        measurement = MeasurementService.get(hash_key)
        measurement.safe_delete()
        return create_success_plain_response(status_text=f"Measurement {hash_key} removed")

    @measurement_namespace.expect(measurement_schema.api_model)
    @measurement_namespace.response(HTTPStatus.OK.real, "Edited measurement", measurement_schema.api_model)
    def put(self, hash_key: str):
        """ Edit selected measurement """
        measurement_data = measurement_schema.loads_required(flask.request.data)
        measurement = MeasurementService.put(**measurement_data)
        return create_success_response(data=measurement_schema.serialize(measurement))
