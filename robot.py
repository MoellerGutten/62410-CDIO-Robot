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
                sound = Sound()
                sound.speak('Welcome to the E V 3 dev project!')

                tank_drive = MoveTank(OUTPUT_A, OUTPUT_B)

                # drive in a turn for 5 rotations of the outer motor
                # the first two parameters can be unit classes or percentages.
                tank_drive.on_for_rotations(SpeedPercent(50), SpeedPercent(75), 10)

                # drive in a different turn for 3 seconds
                tank_drive.on_for_seconds(SpeedPercent(60), SpeedPercent(30), 3)

    finally:
        srv.close()

if __name__ == "__main__":
    main()
