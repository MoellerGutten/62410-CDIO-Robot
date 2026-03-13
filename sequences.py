from commands import *
# Never set blocking to true on commands with no expire or it will hang
def bust(speed):
    # TODO: test duration of balls_out
    balls_out(speed=speed, seconds=5, rotations=None, brake=True, block=True)
    balls_in(speed=speed, rotations=None, seconds=None,brake=True, block=False)