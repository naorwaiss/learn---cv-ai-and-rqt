import cv2
import numpy as np

def main():
    # Open the default camera (usually the built-in webcam)
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Couldn't open camera")
        return

    # Capture a frame
    ret, frame = cap.read()

    # Check if the frame was captured successfully
    if not ret:
        print("Error: Couldn't capture frame")
        return

    # Print the dimensions of the image
    height, width, _ = frame.shape
    print("Image size: {}x{}".format(width, height))

    # Encode the image to JPEG format
    _, encoded_img = cv2.imencode('.jpg', frame)

    # Get the size of the encoded image in bytes
    img_size_bytes = len(encoded_img.tobytes())
    print("Image size in bytes:", img_size_bytes)

    # Display the captured image
    cv2.imshow("Captured Image", frame)

    # Wait for a key press and then close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Release the camera
    cap.release()

if __name__ == "__main__":
    main()
