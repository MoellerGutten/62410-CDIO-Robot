from ev3dev2.sound import Sound # pyright: ignore[reportMissingImports]
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B

def forward(speed, rotations, pos, seconds, brake, block):
    from robot import getMotors
    if seconds:
        getMotors().getTankDrive().on_for_seconds(left_speed=speed, right_speed=speed, seconds=seconds, brake=brake, block=block)
    elif rotations:
        getMotors().getTankDrive().on_for_rotations(left_speed=speed, right_speed=speed, rotations=rotations, brake=brake, block=block)
    elif pos:
        getMotors().getTankDrive().on_for_position(left_speed=speed, right_speed=speed, pos=pos, brake=brake, block=block)
    else:
        return
        

def backward(speed, rotations, pos, seconds, brake, block):
    from robot import getMotors
    if seconds:
        getMotors().getTankDrive().on_for_seconds(left_speed=speed, right_speed=speed, seconds=seconds, brake=brake, block=block)
    elif rotations:
        getMotors().getTankDrive().on_for_rotations(left_speed=speed, right_speed=speed, rotations=rotations, brake=brake, block=block)
    elif pos:
        getMotors().getTankDrive().on_for_position(left_speed=speed, right_speed=speed, pos=pos, brake=brake, block=block)
    else:
        return
    

def turn_left(rspeed, lspeed, rotations, pos, seconds, target_angle, brake, block):
    from robot import getMotors
    if  seconds:
        getMotors().getTankDrive().on_for_seconds(-lspeed, -rspeed, seconds, brake, block)
    elif rotations:
        getMotors().getTankDrive().on_for_rotations(-lspeed, -rspeed, rotations, brake, block)
    elif pos:
        getMotors().getTankDrive().on_for_position(-lspeed, -rspeed, pos, brake, block)
    else:
        return
    
def turn_right(rspeed, lspeed, rotations, pos, seconds, target_angle, brake, block):
    from robot import getMotors
    if  seconds:
        getMotors().getTankDrive().on_for_seconds(-lspeed, -rspeed, seconds, brake, block)
    elif rotations:
        getMotors().getTankDrive().on_for_rotations(-lspeed, -rspeed, rotations, brake, block)
    elif pos:
        getMotors().getTankDrive().on_for_position(-lspeed, -rspeed, pos, brake, block)
    else:
        return
    
# Speed is negative because of the gearing on the current robot
def balls_in(speed, rotations, seconds, brake, block):
    from robot import getMotors
    if seconds:
        getMotors().getBallMotor().on_for_seconds(-speed, seconds, brake, block)
    elif rotations:
        getMotors().getBallMotor().on_for_rotations(-speed, rotations, brake, block)
    else:
        # Default in
        getMotors().getBallMotor().on(-speed, brake, block)
    

def balls_out(speed, rotations, seconds, brake, block):
    from robot import getMotors
    if seconds:
        getMotors().getBallMotor().on_for_seconds(speed, seconds, brake, block)
    elif rotations:
        getMotors().getBallMotor().on_for_rotations(speed, rotations, brake, block)
    else:
        # Default out
        getMotors().getBallMotor().on(speed, brake, block)


def panic(brake):
    from robot import getMotors
    getMotors().getTankDrive().off([LargeMotor(OUTPUT_A), LargeMotor(OUTPUT_B)],brake)

def balls_off(brake, block):
    from robot import getMotors
    getMotors().getBallMotor().stop()

def talk_function(talk):
    sound = Sound()
    sound.speak(talk)
