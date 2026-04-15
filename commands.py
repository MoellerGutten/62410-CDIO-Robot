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

    # Calibrate the gyro to eliminate drift, and to initialize the current angle as 0
    tank_drive.gyro.calibrate()
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
    

def turn_left(rspeed, lspeed, rotations, pos, seconds, target_angle, brake, block):
    if  seconds:
        tank_drive.on_for_seconds(lspeed, 0, seconds, brake, block)
    elif rotations:
        tank_drive.on_for_rotations(lspeed, 0, rotations, brake, block)
    elif pos:
        tank_drive.on_for_position(lspeed, 0, pos, brake, block)
    else:
        return
    
def turn_right(rspeed, lspeed, rotations, pos, seconds, target_angle, brake, block):
    if  seconds:
        tank_drive.on_for_seconds(0, rspeed, seconds, brake, block)
    elif rotations:
        tank_drive.on_for_rotations(0, rspeed, rotations, brake, block)
    elif pos:
        tank_drive.on_for_position(0, rspeed, pos, brake, block)
    else:
        return

def turn(speed, rspeed, lspeed, rotations, pos, seconds, target_angle, brake, block):
    if target_angle:
        try:
            # TODO: This is always blocking. Should be removed or handled otherwise because the gyro doesnt work lmao
            tank_drive.turn_degrees(speed=speed, target_angle=target_angle, brake=brake)
            angle, rate = tank_drive.gyro.angle_and_rate
            print("Gyro - Angle: " + str(angle) + "deg, Rate: " + str(rate) + "deg/s")
        except OSError:
            # Gyro is temporarily inaccessible (being used by main thread)
            pass

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


def panic(brake):
    tank_drive.off([LargeMotor(OUTPUT_A), LargeMotor(OUTPUT_B)],brake)

def balls_off(brake, block):
    ballMotor.stop()

def talk_function(talk):
    sound = Sound()
    sound.speak(talk)
