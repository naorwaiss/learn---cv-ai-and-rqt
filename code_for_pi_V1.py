import sys
import socket
import threading
import time
import numpy as np
import cv2
import struct

class Server:
    def __init__(self):
        self.server_ip = "192.168.1.193"
        self.server_port = 5005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.server_ip, self.server_port))
        self.running = True
        self.command = 0
        self.size_of_data = 0
        self.activate_button = 0  # 0 not activate 1 activate
        self.max_data_send = 15000

    def sort_data(self, data):
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
        self.controller = 0  # 0 is not activated, 1 is activated
        self.square_done = False
        self.controller = 0  # 0 is not activate 1 is activate

    def draw_square_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.square = [(x, y), (x, y)]  # Initialize square with the first corner
            self.square_done = False
        elif event == cv2.EVENT_MOUSEMOVE and flags & cv2.EVENT_FLAG_LBUTTON:
            self.square[1] = (x, y)  # Update second corner as the mouse moves
        elif event == cv2.EVENT_LBUTTONUP:
            self.square[1] = (x, y)  # Finalize second corner
            self.square_done = True

    def organize_data(self):
        try:
            command = self.command
            data_size = self.size_of_data  # Use self.size_of_data

            match command:
                case 1:
                    self.running = False
                    print(f"Server ready to receive big data at size {data_size}")

                    # Start loop to get the data
                    num_of_chunks = int(data_size // self.max_data_send) + 1
                    receive_image = bytearray()  # Initialize as bytes

                    for i in range(num_of_chunks):
                        if i == (num_of_chunks - 1):  # Handling the last chunk
                            data_remain = data_size - (self.max_data_send * i)
                            print(f"last_data {data_remain}")
                            received_data, addr = self.sock.recvfrom(data_remain)
                        else:
                            received_data, addr = self.sock.recvfrom(self.max_data_send)

                        # Append received data to the image data
                        receive_image.extend(received_data)

                        time.sleep(0.1)  # Optionally add a delay to control the rate of data reception

                    print(f"len of the image is: {len(receive_image)}")
                    # Decode received image data
                    nparr = np.frombuffer(receive_image, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    # Check if image decoding was successful
                    if image is not None:
                        print("Decoded image shape:", image.shape)  # Debug print

                        # Register mouse callback for drawing square
                        cv2.namedWindow('Received Image')
                        cv2.setMouseCallback('Received Image', self.draw_square_callback)

                        while True:
                            if self.square_done:
                                # Create a copy of the image to draw on
                                image_with_square = image.copy()

                                # Draw the square
                                cv2.rectangle(image_with_square, self.square[0], self.square[1], (0, 255, 0), 2)
                                print("Square coordinates:", self.square)  # Print square coordinates

                                # Display the image with the square
                                cv2.imshow('Received Image', image_with_square)

                                # Close the square window after 3 seconds
                                cv2.waitKey(3000)
                                cv2.destroyAllWindows()
                                break

                            else:
                                # Display the original image without the square
                                cv2.imshow('Received Image', image)

                            key = cv2.waitKey(1)
                            if key == 27:  # Esc key to exit
                                break

                    else:
                        print("Failed to decode image.")

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

def background_thread(operation, server):
    server_ip = server.server_ip
    server_port = server.server_port

    print("Background thread started.")
    while True:
        user_input = input("Press 'n' to stop the server or 'c' to continue: ")
        if user_input.lower() == 'n':
            operation.stop()
            sys.exit()
        elif user_input.lower() == 'c':
            # Send "Hi" to the client
            send_data_to_client("Hi", (server_ip, server_port))

            # Set controller flag to 1
            operation.controller = 1
            time.sleep(3)

            # Reset controller flag to 0
            operation.controller = 0
        else:
            print("Invalid input. Press 'n' to stop the server or 'c' to continue.")

def send_data_to_client(data, client_address):
    operation.sock.sendto(data.encode("utf-8"), client_address)
    # At this point need to open 2 computers

if __name__ == "__main__":
    operation = Operation()
    operation.run()
    background_thread = threading.Thread(target=background_thread, args=(operation, operation))  # Pass both operation and server instances
    background_thread.start()
