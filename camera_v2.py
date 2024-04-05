import cv2
import imutils
import asyncio
import socket
import time


class ObjectTracker:
    def __init__(self, source=None, server_ip="127.0.0.1", server_port=5005):
        self.video = cv2.VideoCapture(source)
        self.frame = None
        self.BB = None
        self.arm = 0
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

            # Calculate image size
            frame_size_bytes = len(self.frame.tobytes())

            print(f"Size of the image: {frame_size_bytes} bytes")

            # Send command and image size
            command_size_data = f"{1:02}{frame_size_bytes:08}".encode("utf-8")
            self.client_socket.sendto(command_size_data, (self.server_ip, self.server_port))
            time.sleep(2)

            # Send image data
            _, frame_encoded = cv2.imencode('.jpg', self.frame)
            frame_bytes = frame_encoded.tobytes()
            self.client_socket.sendto(frame_bytes, (self.server_ip, self.server_port))

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
    await tracker.process_frames()


if __name__ == "__main__":
    asyncio.run(main())
