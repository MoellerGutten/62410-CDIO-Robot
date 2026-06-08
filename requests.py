from robot import getMotors
from protocol import RequestName

tank_drive = getMotors().getTankDrive()
ballMotor = getMotors().getBallMotor()


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
    return (tank_drive.left_motor.speed, tank_drive.right_motor.speed)


def getIsRunning():
    return (tank_drive.left_motor.is_running, tank_drive.right_motor.is_running)


def getIsRamping():
    return (tank_drive.left_motor.is_ramping, tank_drive.right_motor.is_ramping)


def getIsHolding():
    return (tank_drive.left_motor.is_holding, tank_drive.right_motor.is_holding)


def getIsOverloaded():
    return (tank_drive.left_motor.is_overloaded, tank_drive.right_motor.is_overloaded)