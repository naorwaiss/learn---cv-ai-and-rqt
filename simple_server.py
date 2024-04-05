import serial

# Define the serial port and baud rate
ser = serial.Serial('/dev/ttyACM0', 9600)

try:
    while True:
        # Read data from the serial port
        data = ser.readline().decode().strip()

        # Print the received data
        print(data)

except KeyboardInterrupt:
    # Close the serial port when the program is interrupted
    ser.close()
