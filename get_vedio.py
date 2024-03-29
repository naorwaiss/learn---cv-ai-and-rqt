import socket
import cv2
import pickle
import struct


class VideoServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('192.168.1.193', 8080))
        self.server_socket.listen(0)
        self.client_socket = None

    def start(self):
        self.client_socket, _ = self.server_socket.accept()
        self.receive_video()

    def receive_video(self):
        data = b""
        payload_size = struct.calcsize("L")

        while True:
            while len(data) < payload_size:
                data += self.client_socket.recv(4096)

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_msg_size)[0]

            while len(data) < msg_size:
                data += self.client_socket.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data)
            cv2.imshow('Received Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        self.client_socket.close()
        self.server_socket.close()


if __name__ == "__main__":
    video_server = VideoServer()
    video_server.start()
