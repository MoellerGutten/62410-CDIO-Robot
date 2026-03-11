# robot.py

#!/usr/bin/env python3

import socket
import threading
import time
from ev3dev2.sound import Sound # pyright: ignore[reportMissingImports]
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank
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
                
                if len(arguments) == 2:
                    if arguments[0] == "left":
                        global monitoring
                        monitoring = True
                        monitor_thread = threading.Thread(target=monitor_gyro, args=(tank_drive.gyro), daemon=True)
                        monitor_thread.start()
                        # Pivot left
                        tank_drive.turn_degrees(
                            speed=SpeedPercent(100),
                            target_angle=int(arguments[1])
                        )
                        monitoring = False
                        monitor_thread.join(timeout=1)
                    elif arguments[0] == "right":
                        monitoring = True
                        monitor_thread = threading.Thread(target=monitor_gyro, args=(tank_drive.gyro,), daemon=True)
                        monitor_thread.start()
                        # Pivot right
                        tank_drive.turn_degrees(
                            speed=SpeedPercent(30),
                            target_angle=-int(arguments[1])
                        )
                        monitoring = False
                        monitor_thread.join(timeout=1)
                else:
                    if arguments[0] == "left":
                        tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(-100), 3)

                    elif arguments[0] == "right":
                        tank_drive.on_for_rotations(SpeedPercent(-100), SpeedPercent(100), 3)

                    elif arguments[0] == "forward":
                        tank_drive.on_for_rotations(SpeedPercent(100), SpeedPercent(100), 5, False, False)

                    elif arguments[0] == "backward":
                        tank_drive.on_for_rotations(SpeedPercent(-100), SpeedPercent(-100), 5, False, False)
                    elif arguments[0] == "softright":
                        tank_drive.on_for_rotations(SpeedPercent(50), SpeedPercent(100), 10)
                    elif arguments[0] == "softleft":
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
