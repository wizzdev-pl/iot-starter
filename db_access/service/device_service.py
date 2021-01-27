from pynamodb.pagination import ResultIterator
import pynamodb.exceptions

import common.errors
from service.base_service import BaseService, ItemNotUnique
from model.device_model import DeviceModel, DeviceTypeModel, DeviceGroupModel


class DeviceService(BaseService):
    model_class = DeviceModel

    @classmethod
    def create_device(cls,
                      device_id: str,
                      description: str,
                      device_type: str = "Unprovided",
                      device_group: str = "Unprovided",
                      settings: str = None,
                      **kwargs
                      ) -> DeviceModel:
        try:
            result = cls.create_with_condition(
                device_id=device_id,
                description=description,
                device_type=device_type,
                device_group=device_group,
                settings=settings or {},

                condition=cls.model_class.device_id.does_not_exist(),
                error_message=f'Device with specified id ("{device_id}") already exists!'
            )
        except ItemNotUnique:
            # Allow to overwrite device entry in database
            device = cls.get(hash_key=device_id)
            device.description = description
            device.device_type = device_type
            device.device_group = device_group
            device.settings = settings
            device.save()
            result = device

        DeviceGroupService.create_device_group_if_not_exist(
            device_group=device_group,
            description="Created automatically during adding new device process"
        )
        DeviceTypeService.create_device_type_if_not_exist(
            device_type=device_type,
            description="Created automatically during adding new device process"
        )
        return result

    @classmethod
    def get_device_by_id(cls, device_id) -> DeviceModel:
        return DeviceModel.get(hash_key=device_id)

    @classmethod
    def check_if_device_exists(cls, device_id) -> bool:
        return cls.check_if_exists(hash_key=device_id)

    @classmethod
    def get_devices_by_device_type(cls, device_type: str) -> ResultIterator:
        return cls.scan(DeviceModel.device_type.startswith(device_type) & DeviceModel.device_type.endswith(device_type))

    @classmethod
    def get_devices_by_device_group(cls, device_group: str) -> ResultIterator:
        return cls.scan(DeviceModel.device_group.startswith(device_group) & DeviceModel.device_group.endswith(device_group))


class DeviceTypeService(BaseService):
    model_class = DeviceTypeModel

    @classmethod
    def create_device_type(cls,
                           device_type: str,
                           description: str = None
                           ) -> DeviceTypeModel:
        return cls.create_with_condition(
            device_type=device_type,
            description=description,

            condition=cls.model_class.device_type.does_not_exist(),
            error_message=f'Device Type with specified id ("{device_type}") already exists!'
        )

    @classmethod
    def create_device_type_if_not_exist(cls, device_type: str, description: str = None) -> DeviceTypeModel:
        try:
            return cls.create_device_type(device_type=device_type, description=description)
        except (pynamodb.exceptions.PutError, common.errors.ItemNotUnique):
            pass

    @classmethod
    def get_device_type_by_id(cls, device_type: str):
        return cls.get(hash_key=device_type)

    @classmethod
    def check_if_device_type_exists(cls, device_type: str) -> bool:
        return cls.check_if_exists(hash_key=device_type)


class DeviceGroupService(BaseService):
    model_class = DeviceGroupModel

    @classmethod
    def create_device_group(cls, device_group: str, description: str = None) -> DeviceGroupModel:
        return cls.create_with_condition(
            device_group=device_group,
            description=description,

            condition=cls.model_class.device_group.does_not_exist(),
            error_message=f'Device Group with specified id ("{device_group}") already exists!'
        )

    @classmethod
    def create_device_group_if_not_exist(cls, device_group: str, description: str = None) -> DeviceGroupModel:
        try:
            return cls.create_device_group(device_group=device_group, description=description)
        except (pynamodb.exceptions.PutError, common.errors.ItemNotUnique):
            pass

    @classmethod
    def get_device_group_by_id(cls, device_group: str):
        return cls.get(hash_key=device_group)

    @classmethod
    def check_if_device_group_exists(cls, device_group: str) -> bool:
        return cls.check_if_exists(hash_key=device_group)
