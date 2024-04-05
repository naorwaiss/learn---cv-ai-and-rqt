import socket

def main():
    HOST = '127.0.0.1'  # Replace with the IP address or hostname of the server
    PORT = 5005        # Replace with the port number the server is listening on
    message = "02000456"

    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Connect to the server
        s.connect((HOST, PORT))

        # Send the message
        s.sendall(message.encode())

    print("Message sent successfully")

if __name__ == "__main__":
    main()
