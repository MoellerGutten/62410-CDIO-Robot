# robot.py

import socket
from ev3dev2.sound import Sound
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds

HOST = ""          # empty string = listen on all interfaces
PORT = 9999        # pick any unused port >1024

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
                text = data.decode("utf-8").strip()
                print("Received:", text)
                
                # Example: echo back acknowledgement
                reply = ("ACK: " + text + "\n").encode("utf-8")
                conn.sendall(reply)
                

                tank_drive = MoveTank(OUTPUT_A, OUTPUT_B)

                if text == "left":
                    tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(-100), 1)
                
                if text == "right":
                    tank_drive.on_for_rotations(SpeedPercent(-100), SpeedPercent(100), 1)

                if text == "forward":
                    tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(100), 5)
                
                else:
                    sound = Sound()
                    sound.speak('Jarvis, jerk it a little')
                    tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(100), 0.1)
                    tank_drive.on_for_rotations(SpeedPercent(-100), SpeedPercent(-100), 0.1)
                    tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(100), 0.1)
                    tank_drive.on_for_rotations(SpeedPercent(-100), SpeedPercent(-100), 0.1)
                    tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(100), 0.1)
                    tank_drive.on_for_rotations(SpeedPercent(-100), SpeedPercent(-100), 0.1)
                    tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(100), 0.1)
                    tank_drive.on_for_rotations(SpeedPercent(-100), SpeedPercent(-100), 0.1)
                    tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(100), 0.1)
                    tank_drive.on_for_rotations(SpeedPercent(-100), SpeedPercent(-100), 0.1)
                    tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(100), 0.1)
                    tank_drive.on_for_rotations(SpeedPercent(-100), SpeedPercent(-100), 0.1)

        

    finally:
        srv.close()

if __name__ == "__main__":
    main()
