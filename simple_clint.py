import socket
import time

# Server IP and port
server_ip = "127.0.0.1"
server_port = 8008

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to an available port on localhost
sock.bind(("localhost", 0))

while True:
    # Send "hello world" message to the server
    message = "hello world"
    sock.sendto(message.encode("utf-8"), (server_ip, server_port))
    print("Sent message to server:", message)

    # Add a delay before sending the next message
    time.sleep(1)

# Close the socket
sock.close()
