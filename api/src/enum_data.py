from enum import Enum, unique


@unique
class AccessLevelEnum(Enum):
    OWNER = 'Owner'
    GUEST = 'Guest'
    NONE = 'None'
    CK_ONLY = 'Contactless Key Only'
    FP_ONLY = 'Fingerprint Only'


@unique
class DeviceTypeEnum(Enum):
    LOCK = 'lock'
    HUB = 'Guest'
    WA = 'window actuator'


@unique
class AccessScheduleEnum(Enum):
    ALWAYS = 'Always'
    RECURRING = 'Recurring'
    TEMPORARY = 'Temporary'


@unique
class MobileNumPageCallScenarioEnum(Enum):
    LOGIN = 'login'
    CREATE_CONTACT = 'create_contact'


@unique
class RecurringTimePageCallScenarioEnum(Enum):
    Modify = ''
    CREATE_CONTACT = 'access_schedule_rec_'

@unique
class TemporaryTimePageCallScenarioEnum(Enum):
    Modify = ''
    CREATE_CONTACT = 'access_schedule_temp_'


@unique
class CountryEnum(Enum):
    CHINA = 'China'
    AUSTRALIA = 'Australia'
    IRELAND = 'Ireland'
    SWEDEN = 'Sweden'
    UK = 'United Kingdom'

@unique
class CountryCodeEnum(Enum):
    CHINA = '+86'
    AUSTRALIA = '+61'
    IRELAND = '+353'
    SWEDEN = '+46'
    UK = '+44'


@unique
class RegisterStatus(Enum):
    NOT_REGISTERED = 'Not Registered'
    ON = 'On'
    OFF = 'Off'
    REGISTERED = 'Registered'


@unique
class InviteOptionEnum(Enum):
    VIA_MOBILE_NUM = 'Invite via Mobile Number'
    VIA_CONTACTS = 'Invite from Contacts'


@unique
class DecorateNameEnum(Enum):
    TAG_ATTR = '%tags'
    TAG_CLS_NAME = '%cls_name'


class CalibrationEnum(Enum):
    LOCK_FLIPUP = 'lock/flipUp'
    LOCK_FLIPDOWN = 'lock/flipDown'
    LOCK_CALIBRATION = 'lock/calibration'
    LOCK_STATUS = 'lock/status'
    DOOR_STATUS = 'door/status'
    LOCK_OPEN = 'lock/open'
    LOCK_CLOSE = 'lock/close'
    LOCK_JUST_OPEN = 'lock/justOpen'
    LOCK_JUST_CLOSE = 'lock/justClose'
    LOCK_FULLY_OPEN = 'lock/fullyOpen'
    LOCK_FULLY_CLOSE = 'lock/fullyClose'
    DOOR_OPEN = 'door/open'
    DOOR_CLOSE = 'door/close'
    DOOR_AJAR = 'door/ajar'
    FORCE_CALIBRATION = 'lock/forceCalibration'


class LockAndDoorStatus(Enum):
    LOCK_INIT = -1
    LOCK_UNKNOWN = 0
    LOCK_UNLOCK = 1
    LOCK_LOCK = 2
    LOCK_JAM = 3
    LOCK_LATCH = 4
    LOCK_UNLATCH = 5
    DOOR_INIT = -1
    DOOR_UNKNOWN = 0
    DOOR_OPEN = 1
    DOOR_CLOSED = 2
    DOOR_AJAR = 3
    JIG_ON = 1
    JIG_OFF = 0

class WindowActuatorStatusEnum(Enum):
    WA_FULL = 'Full'
    WA_HALF = 'Half'
    WA_VENT = 'Vent'
    WA_CLOSED = 'Closed'

class LatchTiming(Enum):
    SEC_3 = '3'
    SEC_5 = '5'
    SEC_10 = '10'
    SEC_20 = '20'
    SEC_30 = '30'



