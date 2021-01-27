from .model.base_model import Model
from .model.base_model import AuditModel
from .model.measurement_model import MeasurementModel
from .model.measurement_model import MeasurementTypeModel
from .model.device_model import DeviceModel
from .model.device_model import DeviceGroupModel
from .model.device_model import DeviceTypeModel

from .service.base_service import BaseService
from .service.device_service import DeviceService
from .service.device_service import DeviceGroupService
from .service.device_service import DeviceTypeService
from .service.measurement_service import MeasurementService
from .service.measurement_service import MeasurementTypeService

from .common.config import *
from .common.errors import *
from .common.util import *

# Create tables
create_table(MeasurementModel)
create_table(MeasurementTypeModel)
create_table(DeviceModel)
create_table(DeviceGroupModel)
create_table(DeviceTypeModel)
