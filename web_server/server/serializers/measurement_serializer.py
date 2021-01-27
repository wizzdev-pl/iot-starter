from core.serializer import serializer_factory
from model.measurement_model import MeasurementTypeModel, MeasurementModel


MeasurementSerializer = serializer_factory(MeasurementModel)
MeasurementTypeSerializer = serializer_factory(MeasurementTypeModel)

