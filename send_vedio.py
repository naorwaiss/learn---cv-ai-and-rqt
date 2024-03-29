import socket
import cv2
import pickle
import struct

class VideoClientUDP:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.vid = cv2.VideoCapture(0)

    def start(self):
        self.send_video()

    def send_video(self):
        while True:
            _, frame = self.vid.read()
            data = pickle.dumps(frame)
            size = struct.pack("L", len(data))
            self.client_socket.sendto(size + data, (self.server_ip, 8080))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.vid.release()
        cv2.destroyAllWindows()
        self.client_socket.close()

if __name__ == "__main__":
    client = VideoClientUDP('192.168.1.193')  # Replace '127.0.0.1' with the server's IP address
    client.start()
