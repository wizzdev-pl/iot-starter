class IotDbBaseException(Exception):
    pass


class ItemNotUnique(IotDbBaseException):
    pass


class ItemDoesNotExist(IotDbBaseException):
    pass
