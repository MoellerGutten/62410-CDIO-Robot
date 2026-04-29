#!/usr/bin/env python3

import signal
import atexit
import socket as socket
from commands import *
from sequences import *
from protocol import InstructionType, Acknowledgement, serialize_ack, parse_message, CommandName, SequenceName

HOST = ""          # empty string = listen on all interfaces
PORT = 9999        # pick any unused port >1024

# Global flag to control gyro monitoring thread
monitoring = False

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

    print("EV3 server listening on port", PORT)
   

    try:
        conn, addr = srv.accept()
        _conn = conn
        print("Connected by", addr)

        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                msg = data.decode("utf-8").strip()
                # Debug
                print(msg)
                msg = parse_message(msg)
                
                cmd = msg.instruction.name
                type = msg.instruction.type
                args = msg.instruction.args

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
                    pass
                    # TODO: add request functions here
                else:
                    reply = serialize_ack(Acknowledgement('NAK', data=["unknown_type", str(cmd)])).encode("utf-8")
                    conn.sendall(reply)

                reply = serialize_ack(Acknowledgement('ACK', data=["command", str(cmd)])).encode("utf-8")
                conn.sendall(reply)

                if type == InstructionType.COMMAND:
                    if cmd == CommandName.FORWARD:
                        forward(args.speed, args.rotations, args.position, args.seconds, args.brake, args.block)
                    elif cmd == CommandName.BACKWARD and args.speed and (args.rotations or args.position or args.seconds):
                        backward(args.speed, args.rotations, args.position, args.seconds, args.brake, args.block)
                    elif cmd == CommandName.TANK_LEFT:
                        turn_left(args.lspeed, args.rspeed, args.rotations, args.position, args.seconds, args.target_angle, args.brake, args.block)
                    elif cmd == CommandName.TANK_RIGHT:
                        turn_right(args.lspeed, args.rspeed, args.rotations, args.position, args.seconds, args.target_angle, args.brake, args.block)
                    elif cmd == CommandName.BALL_IN:
                        balls_in(args.speed, args.rotations, args.seconds, args.brake, args.block)
                    elif cmd == CommandName.BALL_OUT:
                        balls_out(args.speed, args.rotations, args.seconds, args.brake, args.block)
                    elif cmd == CommandName.BALL_OFF:
                        balls_off(args.brake, args.block)
                    elif cmd == CommandName.PANIC:
                        panic(args.brake)
                    elif cmd == CommandName.TALK:
                        talk_function(args.talk)
                elif type == InstructionType.SEQUENCE:
                        if cmd == "bust":
                            bust(args.speed)
                elif type == InstructionType.REQUEST:
                    pass
                    # TODO: add request functions here


    finally:
        srv.close()

if __name__ == "__main__":
    main()