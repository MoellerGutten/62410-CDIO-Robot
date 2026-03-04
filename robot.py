# robot.py

import socket
from ev3dev2.sound import Sound
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
from ev3dev2.sensor.lego import GyroSensor


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
    tank_drive = MoveTank(OUTPUT_A, OUTPUT_B)

        # Initialize the tank's gyro sensor
    tank_drive.gyro = GyroSensor()

    # Calibrate the gyro to eliminate drift, and to initialize the current angle as 0
    tank_drive.gyro.calibrate()

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

                arguments = text.split(";")

                conn.sendall(reply)
                print(tank_drive.gyro.angle_and_rate)
                
                if len(arguments) == 2:
                    if arguments == "left":
                        # Pivot 30 degrees
                        tank_drive.turn_degrees(
                            speed=SpeedPercent(100),
                            target_angle=-arguments[1]
                        )
                    elif arguments == "right":
                        # Pivot 30 degrees
                        tank_drive.turn_degrees(
                            speed=SpeedPercent(30),
                            target_angle=arguments[1]
                        )
                
                if arguments == "left":
                    tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(-100), 3)

                elif arguments == "right":
                    tank_drive.on_for_rotations(SpeedPercent(-100), SpeedPercent(100), 3)

                elif arguments == "forward":
                    tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(100), 5, False, False)

                elif arguments == "backward":
                    tank_drive.on_for_rotations(SpeedPercent(-100), SpeedPercent(-100), 5, False, False)
                elif arguments == "softright":
                    tank_drive.on_for_rotations(SpeedPercent(50), SpeedPercent(100), 10)
                elif arguments == "softleft":
                    tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(50), 10)

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
