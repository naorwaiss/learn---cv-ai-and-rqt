import cv2
import imutils
import asyncio
import socket
import time
import threading


class ObjectTracker:
    def __init__(self, source=None, server_ip="127.0.0.1", server_port=5005):
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


    def receive_messages(self):
        while True:
            try:
                # Adjust the buffer size according to the expected size of messages
                data, _ = self.client_socket.recvfrom(1024)  # Adjust the buffer size as needed
                dec_data = data.decode("utf-8")
                if dec_data.isdigit():
                    print("Decoded data is a number.")
                else:
                    print("Decoded data is not a number.")
            except socket.error as e:
                print("Error receiving message:", e)
                break

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
    await tracker.process_frames()


if __name__ == "__main__":
    asyncio.run(main())
