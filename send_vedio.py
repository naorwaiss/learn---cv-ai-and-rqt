import socket
import cv2
import pickle
import struct

class VideoClient:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.vid = cv2.VideoCapture(0)

    def start(self):
        self.client_socket.connect((self.server_ip, 8080))
        self.send_video()

    def send_video(self):
        while True:
            _, frame = self.vid.read()
            data = pickle.dumps(frame)
            size = struct.pack("L", len(data))
            self.client_socket.sendall(size + data)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.vid.release()
        cv2.destroyAllWindows()
        self.client_socket.close()


if __name__ == "__main__":
        # Replace 'server_ip' with the actual IP address or hostname of the server
    client = VideoClient('192.168.1.193')  # Example: 'localhost' or '192.168.1.100'
    client.start()