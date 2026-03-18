# robot.py

#!/usr/bin/env python3

import socket
import threading
import time
from commands import *
from sequences import *
from ev3dev2.sound import Sound # pyright: ignore[reportMissingImports]
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
from ev3dev2.sensor.lego import GyroSensor


HOST = ""          # empty string = listen on all interfaces
PORT = 9999        # pick any unused port >1024

# Global flag to control gyro monitoring thread
monitoring = False

def monitor_gyro(gyro_sensor, interval=0.2):
    """Continuously print gyro angle while monitoring flag is True"""
    while monitoring:
        try:
            angle, rate = gyro_sensor.angle_and_rate
            print("Gyro - Angle: " + str(angle) + "deg, Rate: " + str(rate) + "deg/s")
        except OSError:
            # Gyro is temporarily inaccessible (being used by main thread)
            pass
        time.sleep(interval)

def main():
    # Create TCP socket
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Reuse address so you can restart quickly
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(1)

    print("EV3 server listening on port", PORT)
   

    try:
        conn, addr = srv.accept()
        print("Connected by", addr)

        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                msg = data.decode("utf-8").strip()
                print("Received:", msg)
                
                # Example: echo back acknowledgement
                # reply = ("ACK: " + msg + "\n").encode("utf-8")
                # conn.sendall(reply)

                instructions = msg.split("&")
                for instruction in instructions:
                    temp = instruction.split(":")
                    if len(temp) < 2:
                        msg = "Invalid format"
                        reply = ("NACK: " + msg + "\n").encode("utf-8")
                        conn.sendall(reply)
                        continue
                    command = temp[0]
                    args = temp[1].split(";")
                    print(args)
                    if len(args) < 11:
                        msg = "Not enough arguments"
                        reply = ("NACK: " + msg + "\n").encode("utf-8")
                        conn.sendall(reply)
                        # Arguments in order:
                        # 1. inst_id, 2. rspeed, 3. lspeed, 4. speed, 5. rotations, 
                        # 6. pos, 7. seconds, 8. turn_angle (for turn_degrees(...) ), 9. brake, 10. block, 11. talk
                    else:
                        if args[0]:
                            inst_id = args[0]
                        else: 
                            inst_id = None
                        if args[1]:
                            rspeed = int(args[1])
                        else:
                            rspeed = None
                        if args[2]:
                            lspeed = int(args[2])
                        else:
                            lspeed = None
                        if args[3]:
                            speed = int(args[3])
                        else:
                            speed = None
                        if args[4]:
                            rotations = float(args[4])
                        else:
                            rotations = None
                        if args[5]:
                            pos = float(args[5])
                        else: 
                            pos = None
                        if args[6]:
                            seconds = float(args[6])
                        else:
                            seconds = None
                        if args[7]:
                            turn_angle = float(args[7])
                        else: 
                            turn_angle = None
                        if args[8]:
                            brake = bool(args[8])
                        else:
                            brake = True
                        if args[9]:
                            block = bool(args[9])
                        # TODO: default blocking?
                        else:
                            block = False
                        if args[10]:
                            talk = args[10]
                        else:
                            talk = "Give me something to say you ass jacker"
                    
                        if command == "c_fwd" and speed and (rotations or pos or seconds):
                            forward(speed, rotations, pos, seconds, brake, block)
                        elif command == "c_bwd" and speed and (rotations or pos or seconds):
                            backward(speed, rotations, pos, seconds, brake, block)
                        elif command == "c_tl":
                            turn_left(speed, lspeed, rspeed, rotations, pos, seconds, turn_angle, brake, block)
                        elif command == "c_tr":
                            turn_right(speed, lspeed, rspeed, rotations, pos, seconds, turn_angle, brake, block)
                        elif command == "c_bin":
                            balls_in(speed, rotations, seconds, brake, block)
                        elif command == "c_bout":
                            balls_out(speed, rotations, seconds, brake, block)
                        elif command == "c_boff":
                            balls_off(brake, block)
                        elif command == "c_t":
                            talk_function(talk)
                        elif command == "s_bust":
                            bust(speed)
                        # TODO: add request functions here
                        else:
                            # TODO: implement send_nack
                            # send_nack(command)
                            msg = "Unrecognized command"
                            reply = ("NACK: " + msg + "\n").encode("utf-8")
                            conn.sendall(reply)
                    reply = ("ACK: " + str(instructions) + "\n").encode("utf-8")
                    conn.sendall(reply)

    finally:
        srv.close()

if __name__ == "__main__":
    main()
