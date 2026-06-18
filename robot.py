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
    global _shutdown_called, _srv, _conn
    if _shutdown_called:
        return
    _shutdown_called = True

    panic(brake=True)
    balls_off(brake=True, block=True)

    # Close server socket to break out of accept()
    if _srv is not None:
        try:
            _srv.close()
        except Exception:
            pass
        _srv = None

    # Close client connection if still open
    if _conn is not None:
        try:
            _conn.close()
        except Exception:
            pass
        _conn = None


def main():
    global _srv, _conn, _shutdown_called
    _shutdown_called = False

    # Register shutdown for signals and normal exit
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    atexit.register(shutdown)

    # Create TCP socket
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(1)
    _srv = srv

    print("EV3 server listening on port", PORT)

    while not _shutdown_called:
        conn = None
        try:
            conn, addr = _srv.accept()
            _conn = conn
            print("Connected by", addr)

            # Handle many commands on this single connection
            with conn:
                while not _shutdown_called:
                    try:
                        if not receive_commands(conn):
                            # Client closed connection; go back to accept next client
                            break
                    except Exception as e:
                        # Log error but keep the connection alive
                        print("Error in receive_commands_loop:", e)
                        # Don't break; continue waiting for next command
        except OSError as e:
            # Expected when _srv.close() is called in shutdown()
            if _shutdown_called:
                break
            print("Unexpected accept error:", e)
        except Exception as e:
            print("Server error:", e)
        finally:
            if conn is not None:
                try:
                    conn.close()
                    print("Standard connection close. Turning off rob")
                    panic(brake=True)
                    balls_off(brake=True, block=True)
                except Exception:
                    pass
            # Do NOT close _srv here

    # shutdown() has already closed _srv and _conn; main just returns


def receive_commands(conn):
    """
    Loop over commands on a single connection:
    - Returns False only when the client closes the connection (data == b"")
    - Returns True on success
    - Never closes conn itself; exceptions are handled externally
    """
    PRESET = current_preset

    while True:
        # Receive one message
        try:
            data = conn.recv(1024)
        except OSError as e:
            # Network error: treat as connection close
            print("recv OSError:", e)
            panic(brake=True)
            balls_off(brake=True, block=True)
            return False

        if not data:
            # Client closed the connection
            return False

        raw_msg = data.decode("utf-8").strip()
        msgs = parse_message(raw_msg)

        for msg in msgs:
            print(repr(msg.instruction) + "\n")
            try:
                cmd = msg.instruction.name
                type = msg.instruction.type
                args = msg.instruction.args
            except Exception as e:
                reply = serialize_ack(Acknowledgement('NAK', data=["unknown_error", str(msg)])).encode("utf-8")
                conn.sendall(reply)
                continue

            # Validate command/sequence/request
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

            # Send ACK/NACK and execute
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