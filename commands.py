from ev3dev2.sound import Sound # pyright: ignore[reportMissingImports]
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
from ev3dev2.sensor.lego import GyroSensor

try:
    tank_drive = MoveTank(OUTPUT_A, OUTPUT_B)
    ballMotor = MediumMotor(OUTPUT_C)

        # Initialize the tank's gyro sensor
    tank_drive.gyro = GyroSensor()
except:
    pass


def forward(speed, rotations, pos, seconds, brake, block):
    if seconds:
        tank_drive.on_for_seconds(left_speed=speed, right_speed=speed, seconds=seconds, brake=brake, block=block)
    elif rotations:
        tank_drive.on_for_rotations(left_speed=speed, right_speed=speed, rotations=rotations, brake=brake, block=block)
    elif pos:
        tank_drive.on_for_position(left_speed=speed, right_speed=speed, pos=pos, brake=brake, block=block)
    else:
        return
        

def backward(speed, rotations, pos, seconds, brake, block):
    if seconds:
        tank_drive.on_for_seconds(left_speed=-speed, right_speed=speed, seconds=seconds, brake=brake, block=block)
    elif rotations:
        tank_drive.on_for_rotations(left_speed=-speed, right_speed=speed, rotations=rotations, brake=brake, block=block)
    elif pos:
        tank_drive.on_for_position(left_speed=-speed, right_speed=speed, pos=pos, brake=brake, block=block)
    else:
        return
    
# TODO: Should change to target_angle when protocol is updated
def turn_left(speed, rspeed, lspeed, rotations, pos, seconds, turn_angle, brake, block):
    # Calibrate the gyro to eliminate drift, and to initialize the current angle as 0
    tank_drive.gyro.calibrate()
    if turn_angle:
        tank_drive.turn_left(speed=speed, turn_angle=turn_angle, brake=brake)
    elif  seconds:
        tank_drive.on_for_seconds(lspeed, rspeed, seconds, brake, block)
    elif rotations:
        tank_drive.on_for_rotations(lspeed, rspeed, rotations, brake, block)
    elif pos:
        tank_drive.on_for_position(lspeed, rspeed, pos, brake, block)
    else:
        return
    

def turn_right(speed, rspeed, lspeed, rotations, pos, seconds, turn_angle, brake, block):
    # Calibrate the gyro to eliminate drift, and to initialize the current angle as 0
    tank_drive.gyro.calibrate()
    if turn_angle:
        tank_drive.turn_left(speed=speed, turn_angle=turn_angle, brake=brake)
    elif  seconds:
        tank_drive.on_for_seconds(lspeed, rspeed, seconds, brake, block)
    elif rotations:
        tank_drive.on_for_rotations(lspeed, rspeed, rotations, brake, block)
    elif pos:
        tank_drive.on_for_position(lspeed, rspeed, pos, brake, block)
    else:
        return
    
# Speed is negative because of the gearing on the current robot
def balls_in(speed, rotations, seconds, brake, block):
    if seconds:
        ballMotor.on_for_seconds(speed, seconds, brake, block)
    elif rotations:
        ballMotor.on_for_rotations(speed, rotations, brake, block)
    else:
        # Default in
        ballMotor.on(speed, brake, block)
    

def balls_out(speed, rotations, seconds, brake, block):
    if seconds:
        ballMotor.on_for_seconds(-speed, seconds, brake, block)
    elif rotations:
        ballMotor.on_for_rotations(-speed, rotations, brake, block)
    else:
        # Default out
        ballMotor.on(-speed, brake, block)

def balls_off(brake, block):
    ballMotor.off()

def talk_function(talk):
    sound = Sound()
    sound.speak(talk)
