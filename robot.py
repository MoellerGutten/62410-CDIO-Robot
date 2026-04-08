#!/usr/bin/env python3

import socket as socket
from commands import *
from sequences import *
from protocol import InstructionType, Acknowledgement, serialize_ack, parse_message, CommandName


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
                # Debug
                print(msg)
                msg = parse_message(msg)
                
                cmd = msg.instruction.name
                type = msg.instruction.type
                args = msg.instruction.args
                if type == InstructionType.COMMAND:
                    if cmd == CommandName.FORWARD:
                        forward(args.speed, args.rotations, args.position, args.seconds, args.brake, args.block)
                    elif cmd == CommandName.BACKWARD and args.speed and (args.rotations or args.position or args.seconds):
                        backward(args.speed, args.rotations, args.position, args.seconds, args.brake, args.block)
                    elif cmd == CommandName.TANK_LEFT:
                        turn_left(args.speed, args.lspeed, args.rspeed, args.rotations, args.position, args.seconds, args.target_angle, args.brake, args.block)
                    elif cmd == CommandName.TANK_RIGHT:
                        turn_right(args.speed, args.lspeed, args.rspeed, args.rotations, args.position, args.seconds, args.target_angle, args.brake, args.block)
                    elif cmd == CommandName.BALL_IN:
                        balls_in(args.speed, args.rotations, args.seconds, args.brake, args.block)
                    elif cmd == CommandName.BALL_OUT:
                        balls_out(args.speed, args.rotations, args.seconds, args.brake, args.block)
                    elif cmd == CommandName.BALL_OFF:
                        balls_off(args.brake, args.block)
                    elif cmd == CommandName.TALK:
                        talk_function(args.talk)
                    else:
                        reply = serialize_ack(Acknowledgement('NAK', data=["unknown_command", str(cmd)])).encode("utf-8")
                        conn.sendall(reply)
                elif type == InstructionType.SEQUENCE:
                        if cmd == "bust":
                            bust(args.speed)
                        else:
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

    finally:
        srv.close()

if __name__ == "__main__":
    main()
