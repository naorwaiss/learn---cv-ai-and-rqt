import cv2
import imutils
import pyrealsense2.pyrealsense2 as rs

#missiom
  """ need to add:
  1) when the object leave the frame dont do track again 
  2) when the object left -- you can do the ock again 
  3) need to send the vedio 
  """


class ObjectTracker:
    def __init__(self, source=None):
        # Initialize the tracker (CSRT)
        self.tracker = cv2.TrackerCSRT_create()

        # Initialize the video capture object
        if source is None:
            self.video = cv2.VideoCapture(0)
        else:
            self.video = cv2.VideoCapture(source)

        # Read the first frame
        _, self.frame = self.video.read()
        # Resize the frame
        self.frame = imutils.resize(self.frame, width=720)
        self.BB = None
        self.arm = 0

        # Start camera automatically
        self.simple_camera()

    def simple_camera(self):
        while True:
            # Read a new frame
            ret, frame = self.video.read()
            if not ret:
                break

            # Display the frame
            cv2.imshow('Frame', frame)

            # Check for '1' key press to freeze and select ROI
            key = cv2.waitKey(1) & 0xFF
            print("to start the vedio proccesing need to press 1 - later need to change to botton")
            if key == ord('1'):
                self.frame = frame
                self.arm = 1
                break

    def select_roi(self):
        if self.arm == 1:
            # Select the Region of Interest (ROI)
            self.BB = cv2.selectROI("Frame", self.frame, fromCenter=False, showCrosshair=True)
            print (f"the value of the box {self.BB}")
            # Initialize the tracker with the selected ROI
            self.tracker.init(self.frame, self.BB)

    def track_object(self):
        # Start tracking
        while True:
            # Read a new frame
            ret, frame = self.video.read()
            if not ret:
                break

            # Resize the frame
            frame = imutils.resize(frame, width=720)
            # Update the tracker
            track_success, bbox = self.tracker.update(frame)
            # If tracking is successful, draw bounding box
            if track_success:
                #the x,y is from the right up and not at the center of the frame need to t oconvert
                (x, y, w, h) = [int(v) for v in bbox]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                #print(f"{x},{y},{w},{h}")
            # Display the frame
            cv2.imshow('Frame', frame)
            # Check for 'q' key press to exit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    def run(self):
        # Method to run the tracker
        self.select_roi()
        self.track_object()
        self.video.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Run with webcam
    tracker_webcam = ObjectTracker()
    tracker_webcam.run()
