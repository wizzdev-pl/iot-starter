from core.serializer import serializer_factory
from model.device_model import DeviceModel, DeviceGroupModel, DeviceTypeModel


DeviceSerializer = serializer_factory(DeviceModel)
DeviceGroupSerializer = serializer_factory(DeviceGroupModel)
DeviceTypeSerializer = serializer_factory(DeviceTypeModel)
