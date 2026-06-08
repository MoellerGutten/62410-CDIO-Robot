from protocol import RequestName

def getRequest(cmd):
    if cmd == RequestName.SPEED:
        return getSpeed()
    elif cmd == RequestName.ISRUNNING:
        return getIsRunning()
    elif cmd == RequestName.ISRAMPING:
        return getIsRamping()
    elif cmd == RequestName.ISHOLDING:
        return getIsHolding()
    elif cmd == RequestName.ISOVERLOADED:
        return getIsOverloaded()
    return None

def getSpeed():
    from robot import getMotors
    tank_drive = getMotors().getTankDrive()
    return (tank_drive.left_motor.speed, tank_drive.right_motor.speed)

def getIsRunning():
    from robot import getMotors
    tank_drive = getMotors().getTankDrive()
    return (tank_drive.left_motor.is_running, tank_drive.right_motor.is_running)

def getIsRamping():
    from robot import getMotors
    tank_drive = getMotors().getTankDrive()
    return (tank_drive.left_motor.is_ramping, tank_drive.right_motor.is_ramping)

def getIsHolding():
    from robot import getMotors
    tank_drive = getMotors().getTankDrive()
    return (tank_drive.left_motor.is_holding, tank_drive.right_motor.is_holding)

def getIsOverloaded():
    from robot import getMotors
    tank_drive = getMotors().getTankDrive()
    return (tank_drive.left_motor.is_overloaded, tank_drive.right_motor.is_overloaded)