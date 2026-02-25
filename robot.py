# robot.py
import socket
from ev3dev2 import *
import EV3Brick

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
                EV3Brick.speaker.beep()

    finally:
        srv.close()

if __name__ == "__main__":
    main()
