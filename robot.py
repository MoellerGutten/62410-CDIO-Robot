# robot.py

#!/usr/bin/env python3

import socket
import threading
import time
from commands import *
from sequences import *
from protocol import Instruction, InstructionType, Message, Acknowledgement, serialize_ack, parse_message
"""
from ev3dev2.sound import Sound # pyright: ignore[reportMissingImports]
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
from ev3dev2.sensor.lego import GyroSensor
"""

HOST = ""          # empty string = listen on all interfaces
PORT = 9999        # pick any unused port >1024

# Global flag to control gyro monitoring thread
monitoring = False

def main():
    # Create TCP socket
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Reuse address to restart quickly
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
                msg = parse_message(msg)

                cmd = msg.instruction.name
                type = msg.instruction.type
                args = msg.instruction.args

                if type == InstructionType.COMMAND:
                    if cmd == "c_fwd" :
                        forward(args.speed, args.rotations, args.pos, args.seconds, args.brake, args.block)
                    elif cmd == "c_bwd" and args.speed and (args.rotations or args.pos or args.seconds):
                        backward(args.speed, args.rotations, args.pos, args.seconds, args.brake, args.block)
                    elif cmd == "c_tl":
                        turn_left(args.speed, args.lspeed, args.rspeed, args.rotations, args.pos, args.seconds, args.turn_angle, args.brake, args.block)
                    elif cmd == "c_tr":
                        turn_right(args.speed, args.lspeed, args.rspeed, args.rotations, args.pos, args.seconds, args.turn_angle, args.brake, args.block)
                    elif cmd == "c_bin":
                        balls_in(args.speed, args.rotations, args.seconds, args.brake, args.block)
                    elif cmd == "c_bout":
                        balls_out(args.speed, args.rotations, args.seconds, args.brake, args.block)
                    elif cmd == "c_boff":
                        balls_off(args.brake, args.block)
                    elif cmd == "c_t":
                        talk_function(args.talk)
                    else:
                        reply = serialize_ack(Acknowledgement('NAK', data=["unknown_command", cmd]))
                        conn.sendall(reply)
                elif type == InstructionType.SEQUENCE:
                        if cmd == "s_bust":
                            bust(args.speed)
                        else:
                            reply = serialize_ack(Acknowledgement('NAK', data=["unknown_sequence", cmd]))
                            conn.sendall(reply)
                elif type == InstructionType.REQUEST:
                    pass
                    # TODO: add request functions here
                else:
                    reply = serialize_ack(Acknowledgement('NAK', data=["unknown_type", cmd]))
                    conn.sendall(reply)

            reply = serialize_ack(Acknowledgement('ACK', data=["command", cmd]))
            conn.sendall(reply)

    finally:
        srv.close()

if __name__ == "__main__":
    main()
