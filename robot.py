#!/usr/bin/env python3

import signal
import atexit
import socket as socket
from commands import *
from presets.preset_config import current_preset
from sequences import *
from requests import getRequest
from protocol import InstructionType, Acknowledgement, serialize_ack, parse_message, CommandName, SequenceName, RequestName
from ev3dev2.motor import MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, MoveTank
from log import log

HOST = ""          # empty string = listen on all interfaces
PORT = 9999        # pick any unused port >1024
class Motors:
    def __init__(self):
        try:
            self.tank_drive = MoveTank(OUTPUT_A, OUTPUT_B)
            self.ballMotor = MediumMotor(OUTPUT_C)
        except Exception as e:
            log(repr(e))
            log("Left large motor should be in: Output A\n" \
            "Right large motor should be in: Output B\n" \
            "Ball motor (front) should be in: Output C\n" \
            "\n Double check all connections for loose wires, and try again")

    def getTankDrive(self):
        return self.tank_drive

    def getBallMotor(self):
        return self.ballMotor
     
motors = Motors()

# Global references for cleanup
_srv = None
_conn = None
_shutdown_called = False

def shutdown(signum=None, frame=None):
    global _shutdown_called
    if _shutdown_called:
        return
    _shutdown_called = True

    panic(brake=True)
    balls_off(brake=True, block=True)


def main():
    global _srv, _conn
    from requests import getRequest

    # Register shutdown for signals and normal exit
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    atexit.register(shutdown)

    # Create TCP socket
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Reuse address to restart quickly
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(1)
    _srv = srv

    log("EV3 server listening on port", PORT)
   
    while True:
        try:
            conn, addr = srv.accept()
            _conn = conn
            log("Connected by", addr)

            with conn:
                while True:
                    if receive_commands(conn) == False:
                        break
        finally:
            srv.close()


def receive_commands(conn):
    # Load options for robot (switch motor direction, turn direction, speed modifier etc.)
    PRESET = current_preset
    data = conn.recv(1024)
    if not data:
        return False
    raw_msg = data.decode("utf-8").strip()
    msgs = parse_message(raw_msg)
    for msg in msgs:
        log(repr(msg.instruction) + "\n")
        try:
            cmd = msg.instruction.name
            type = msg.instruction.type
            args = msg.instruction.args
        except:
            reply = serialize_ack(Acknowledgement('NAK', data=["unknown_error", str(msg)])).encode("utf-8")
            conn.sendall(reply)

        # Sends ACK or NACK before starting the instruction below
        if type == InstructionType.COMMAND:
            if cmd not in [CommandName.FORWARD, CommandName.BACKWARD, CommandName.TANK_LEFT, CommandName.TANK_RIGHT, 
                    CommandName.BALL_IN, CommandName.BALL_OUT, CommandName.BALL_OFF, CommandName.PANIC, CommandName.TALK]:
                reply = serialize_ack(Acknowledgement('NAK', data=["unknown_command", str(cmd)])).encode("utf-8")
                conn.sendall(reply)
        elif type == InstructionType.SEQUENCE:
                if cmd not in [SequenceName.EJECT]:
                    reply = serialize_ack(Acknowledgement('NAK', data=["unknown_sequence", str(cmd)])).encode("utf-8")
                    conn.sendall(reply)
        elif type == InstructionType.REQUEST:
            if cmd not in [RequestName.SPEED, RequestName.ISRUNNING, RequestName.ISHOLDING, RequestName.ISRAMPING, RequestName.ISOVERLOADED]:
                reply = serialize_ack(Acknowledgement('NAK', data=["unknown_request", str(cmd)])).encode("utf-8")
                conn.sendall(reply)
        else:
            reply = serialize_ack(Acknowledgement('NAK', data=["unknown_type", str(cmd)])).encode("utf-8")
            conn.sendall(reply)

        # If it is a request, send the request with ack
        if type == InstructionType.REQUEST:
            reply = serialize_ack(Acknowledgement('ACK', data=["data", str(getRequest(cmd))])).encode("utf-8")
            conn.sendall(reply)
        else:
            reply = serialize_ack(Acknowledgement('ACK', data=["command", str(cmd)])).encode("utf-8")
            conn.sendall(reply)

        if type == InstructionType.COMMAND:
            if cmd == CommandName.FORWARD:
                forward(args.speed * int(PRESET.reverse_motor) * PRESET.speed_modifier, args.rotations, args.position, args.seconds, args.brake, args.block)
            elif cmd == CommandName.BACKWARD and args.speed and (args.rotations or args.position or args.seconds):
                backward(args.speed * PRESET.speed_modifier, args.rotations, args.position, args.seconds, args.brake, args.block)
            elif cmd == CommandName.TANK_LEFT:
                if PRESET.reverse_direction:
                    turn_left(args.lspeed * PRESET.speed_modifier, args.rspeed * PRESET.speed_modifier, args.rotations, args.position, args.seconds, args.target_angle, args.brake, args.block)
                else:
                    turn_left(args.rspeed * PRESET.speed_modifier, args.lspeed * PRESET.speed_modifier, args.rotations, args.position, args.seconds, args.target_angle, args.brake, args.block)
            elif cmd == CommandName.TANK_RIGHT:
                if PRESET.reverse_direction:
                    turn_right(args.lspeed * PRESET.speed_modifier, args.rspeed * PRESET.speed_modifier, args.rotations, args.position, args.seconds, args.target_angle, args.brake, args.block)
                else:
                    turn_right(args.rspeed * PRESET.speed_modifier, args.lspeed * PRESET.speed_modifier, args.rotations, args.position, args.seconds, args.target_angle, args.brake, args.block)

            elif cmd == CommandName.BALL_IN:
                balls_in(args.speed * PRESET.speed_modifier, args.rotations, args.seconds, args.brake, args.block)
            elif cmd == CommandName.BALL_OUT:
                balls_out(args.speed * PRESET.speed_modifier, args.rotations, args.seconds, args.brake, args.block)
            elif cmd == CommandName.BALL_OFF:
                balls_off(args.brake, args.block)
            elif cmd == CommandName.PANIC:
                panic(args.brake)
            elif cmd == CommandName.TALK:
                talk_function(args.talk)
        elif type == InstructionType.SEQUENCE:
                if cmd == SequenceName.EJECT:
                    bust(args.speed)

def getMotors():
    return motors

if __name__ == "__main__":
    main()