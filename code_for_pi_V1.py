import base64
import socket
import threading
import time
import numpy as np
import cv2





class Server:
    def __init__(self):
        self.server_ip = "127.0.0.1"
        self.server_port = 5005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.server_ip, self.server_port))
        self.running = True
        self.command = 0
        self.size_of_data = 0
        self.activate_batton= 0 #0 not activate 1 activate

    def sort_data(self, data):
        try:
            decoded_data = data.decode("utf-8")
            sorted_data = sorted(decoded_data.split())  # Sort the words in the received string
            sorted_str = ''.join(sorted_data)  # Join the sorted words without space
            command = int(sorted_str[0:2])
            data_size = int(sorted_str[2:])
            self.command = command
            self.size_of_data = data_size

            #print(f"Sorted data: command={command}, size={data_size}")

        except Exception as e:
            print("Error sorting data:", e)

    def receive_data(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(12)  # Adjust buffer size as needed
                if data:
                    print("start Received camman and data size from:", addr)
                    self.sort_data(data)  # Sort the received data
                    self.organize_data()  # Process the sorted data
            except socket.timeout:
                continue
            except Exception as e:
                print("Error receiving data:", e)

    def run(self):
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()

    def stop(self):
        self.running = False
        self.sock.close()
        print("Server stopped.")




class Operation(Server):
    # This is the main operation that controls all the tasks
    def __init__(self):
        super().__init__()
        self.square = None
        self.square_done = False

    def draw_square_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.square = [(x, y), (x, y)]  # Initialize square with the first corner
            self.square_done = False
        elif event == cv2.EVENT_MOUSEMOVE and flags & cv2.EVENT_FLAG_LBUTTON:
            self.square[1] = (x, y)  # Update second corner as the mouse moves
        elif event == cv2.EVENT_LBUTTONUP:
            self.square[1] = (x, y)  # Finalize second corner
            self.square_done = True

            # Calculate coordinates and dimensions of the square
            x1, y1 = self.square[0]
            x2, y2 = self.square[1]
            square_x = min(x1, x2)
            square_y = min(y1, y2)
            square_w = abs(x2 - x1)
            square_h = abs(y2 - y1)


    def organize_data(self):
        try:
            command = self.command
            data_size = self.size_of_data  # Use self.size_of_data

            match command:
                case 1:
                    self.running = False
                    print(f"Server ready to receive big data at size {data_size}")
                    picture, addr = self.sock.recvfrom(data_size)

                    # Ensure image data is not empty
                    if picture:
                        image_np = np.frombuffer(picture, np.uint8)
                        # Decode image
                        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

                        # Check if image decoding was successful
                        if image is not None:
                            print("Decoded image shape:", image.shape)  # Debug print
                            # Display the image
                            cv2.imshow('Image', image)

                            self.square_done = False
                            cv2.setMouseCallback('Image', self.draw_square_callback)

                            while not self.square_done:
                                if self.square is not None:
                                    img_with_square = image.copy()
                                    cv2.rectangle(img_with_square, self.square[0], self.square[1], (0, 255, 0), 2)
                                    cv2.imshow('Image', img_with_square)
                                cv2.waitKey(1)

                            print(self.square)


                            cv2.destroyAllWindows()
                        else:
                            print("Failed to decode image.")
                    else:
                        print("Received empty image data.")

                    time.sleep(3)

                    self.running = True

                case 2:
                    # Handle command 2
                    print("Received command 2")
                    # Do something for command 2

                # Add more cases as needed
                case _:
                    print("Unknown command:", command)
        except Exception as e:
            print("Error organizing data:", e)






if __name__ == "__main__":
    operation = Operation()
    operation.run()
    input("Press enter to stop the server...")
    operation.stop()
