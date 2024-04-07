import cv2
import imutils
import asyncio
import socket
import threading
import pyrealsense2 as rs
import serial  #read serial from autopilot yoad code


#alot of work at this code -
#1) need to check that the trade not stop and start again after i enter a trhead
#2) need to conver the camera to the code camera - with pyrealsnese and make the to do what yoad code to
#3) need to check the qunqe get can work with trhead
#4) this code need to

class ObjectTracker:
    def __init__(self, source=None, server_ip="192.168.1.121", server_port=5005):
        self.video = cv2.VideoCapture(source)
        self.frame = None
        self.BB = None
        self.arm = 0
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.max_data_send = 15000
        self.send_data = False  # Describe if I send
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True


    async def simple_camera(self):
        while True:
            ret, frame = self.video.read()
            if not ret:
                break

            cv2.imshow('Frame', frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('1'):
                self.frame = frame
                self.arm = 1
                break
    async def get_simple_frame(self):
        #get simple frame from the user
        return



    async def select_roi(self):
        if self.arm == 1:
            self.BB = cv2.selectROI("Frame", self.frame, fromCenter=False, showCrosshair=True)
            self.tracker = cv2.TrackerCSRT_create()
            self.tracker.init(self.frame, self.BB)

            # Encode the frame
            _, frame_encoded = cv2.imencode('.jpg', self.frame)
            frame_bytes = frame_encoded.tobytes()

            # Send command and image size
            command_size_data = f"{1:02}{len(frame_bytes):38}".encode("utf-8")
            print("Command:", command_size_data)
            self.client_socket.sendto(command_size_data, (self.server_ip, self.server_port))
            await asyncio.sleep(2)
            print(len(frame_bytes))
            num_of_chunks = int(len(frame_bytes) // self.max_data_send) + 1
            print(num_of_chunks)

            # Send image data in chunks
            for i in range(num_of_chunks):
                start_idx = i * self.max_data_send
                end_idx = min((i + 1) * self.max_data_send, len(frame_bytes))
                print(start_idx, end_idx)
                chunk_data = frame_bytes[start_idx:end_idx]
                self.client_socket.sendto(chunk_data, (self.server_ip, self.server_port))
                await asyncio.sleep(0.01)  # Add a small delay to avoid flooding the network

            print("Image data sent successfully")

        self.arm = 0

    async def track_object(self):
        while True:
            ret, frame = self.video.read()
            if not ret:
                break

            frame = imutils.resize(frame, width=720)

            if self.tracker is not None:
                track_success, bbox = self.tracker.update(frame)
                if track_success:
                    (x, y, w, h) = [int(v) for v in bbox]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imshow('Frame', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.arm = 0
                self.BB = None
                self.tracker = None
                break
            elif key == ord('1'):
                self.arm = 1
                self.BB = None
                self.tracker = None
                self.frame = frame
                await self.select_roi()

    async def process_frames(self):
        await self.simple_camera()
        await self.select_roi()
        await self.track_object()
        self.video.release()
        cv2.destroyAllWindows()


async def main():
    tracker = ObjectTracker(source=0)
    tracker.receive_thread.start()  # Start the receive_messages() function in a separate thread
    server = server_drone()
    server.start()  # Start the drone server thread
    await tracker.process_frames()













class server_drone(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server_ip = "127.0.0.1"  # this is the server of the drone
        self.server_port = 8008
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.server_ip, self.server_port))
        self.size_of_data = 0
        self.activate_button = 0  # 0 not activate 1 activate
        self.max_data_send = 15000
        self.runing = False


    def sort_data(self, data):
        """
        this function will sort the data that the server recive from the cliant
        it help the script understand where what the command and the size of the data
        """
        try:
            decoded_data = data.decode("utf-8")
            sorted_data = sorted(decoded_data.split())  # Sort the words in the received string
            sorted_str = ''.join(sorted_data)  # Join the sorted words without space
            command = int(sorted_str[0:2])
            data_size = int(sorted_str[2:])
            self.command = command
            self.size_of_data = data_size
            print(f"Command {command}, Data size {data_size}")
        except Exception as e:
            print("Error sorting data:", e)  # at the second time it stack here

        def receive_data(self):
            # at this code I receive data for the server
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(40)  # Adjust buffer size as needed
                    if data:
                        # print("start Received command and data size from:", addr)
                        self.sort_data(data)  # Sort the received data
                        self.organize_data()  # Process the sorted data
                except socket.timeout:
                    continue
                except Exception as e:
                    print("Error receiving data:", e)
        #need to finish this

    def run(self):
        print(f"drone server is start")


if __name__ == "__main__":
    asyncio.run(main())
