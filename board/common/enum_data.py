class CalibrationEnum:
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
    
    cmd = {
        LOCK_OPEN :'FF FF 01 0A 03 29 32 E7 0D 00 00 D0 07 CB', # unlock  3559
        LOCK_CLOSE : 'FF FF 01 0A 03 29 32 8F 12 00 00 D0 07 1E', # lock   4751
        LOCK_JUST_OPEN : 'FF FF 01 0A 03 29 32 B0 0D 00 00 D0 07 02', # just unlock  3504
        LOCK_JUST_CLOSE : 'FF FF 01 0A 03 29 32 50 12 00 00 D0 07 5D', # just lock 4688
        LOCK_FULLY_OPEN : 'FF FF 01 0A 03 29 32 00 0D 00 00 D0 07 B2', # fylly unlock 3328
        LOCK_FULLY_CLOSE : 'FF FF 01 0A 03 29 32 99 14 00 00 D0 07 12' # fully lock 5723
        }
    
class MessageEnum:
    move = b'flag=2' #
    success = b'flag=1'
    fail = b'flag=0'
    

    

    
