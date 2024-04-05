mport sys
from math import cos, sin, pi
from typing import Tuple
import time

import av
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGraphicsOpacityEffect, QLabel
from PyQt5.QtGui import QPainter, QPen, QBrush, QPaintEvent, QImage, QPixmap, QFont, QCloseEvent,QColor
from PyQt5.QtCore import Qt, QPoint, QTimer, QThread, pyqtSignal, pyqtSlot,QObject,pyqtSignal




class TextInstructionLabel(QLabel):
    """
    A label that displays instructional text within the application's GUI, offering guidance or actions to the user.

    :param parent: The parent window for this widget.
    :type parent: QMainWindow
    :param font: The font used to display the label's text.
    :type font: QFont
    :param font_size: The size of the font. Defaults to 12.
    :type font_size: int, optional
    :param color: The color of the text. Defaults to "black".
    :type color: str, optional
    :param text: The text to be displayed by the label. Defaults to an empty string.
    :type text: str, optional
    """

    def __init__(self, parent: QMainWindow, font: QFont = QFont(), font_size: int = 12, color: str = "black",
                 text: str = "") -> None:
        super(TextInstructionLabel, self).__init__(parent)
        self.font = font
        self.font.setFamily("Helvetica")
        self.font.setPointSize(font_size)
        self.color = color
        self.text = text
        self.setStyleSheet(f"color: {self.color};"
                           "background-color: rgba(45, 45, 45, 60);")
        self.setFont(self.font)
        self.setText(self.text)
        self.setAlignment(Qt.AlignCenter)


class SemiCircleWidget(QWidget):
    """
    A widget that displays a semicircle with a dynamically updating ticker based on the robot's angle to help position it.

    :param parent: The parent window for this widget. Defaults to None.
    :type parent: QMainWindow, optional
    :param safe_range: A tuple indicating the safe range of the semicircle. Defaults to (75, 70).
    :type safe_range: Tuple[float, float], optional
    :param ticker_angle: The initial angle of the ticker in degrees. Defaults to 90.
    :type ticker_angle: Int, optional
    """

    def __init__(self, parent: QMainWindow = None, safe_range: Tuple[float, float] = (75, 70),
                 ticker_angle: float = 90) -> None:
        super(SemiCircleWidget, self).__init__(parent)
        self.safe_range = ((180 - safe_range[1] - safe_range[0]) * 16, safe_range[1] * 16)
        self.ticker_angle = ticker_angle  # Angle in degrees where the ticker points
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(50)

    def update_angle(self) -> None:
        """
        Repeatedly called with to modify the ticker's angle and call set_ticker_angle.

        :return: None
        """
        angle = self.ticker_angle - 10.5
        angle = angle % 180
        self.set_ticker_angle(angle)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Handles the widget's painting event, drawing the semicircle, ticker, and arrowhead.

        :param event: The paint event.
        :type event: QPaintEvent
        :return: None
        """
        painter = QPainter(self)
        rect = [0, 0, self.width(), self.height()]

        painter.setBrush(QBrush(Qt.red))
        painter.drawPie(rect[0], rect[1], rect[2], rect[3], self.safe_range[1] + self.safe_range[0],
                        (180 * 16) - (self.safe_range[0] + self.safe_range[1]))
        painter.drawPie(rect[0], rect[1], rect[2], rect[3], 0, self.safe_range[1] + self.safe_range[0])
        painter.setBrush(QBrush(Qt.green))
        painter.drawPie(rect[0], rect[1], rect[2], rect[3], self.safe_range[0], self.safe_range[1])
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawArc(*rect, 0, 180 * 16)

        center_x = int(rect[0] + rect[2] / 2)
        radius = int(rect[2] / 2)
        tick_length = 10
        for angle in range(0, 181, 30):
            radian = angle * (pi / 180)
            outer_x = int(center_x + radius * cos(radian))
            outer_y = int(rect[1] + radius - radius * sin(radian))
            inner_x = int(center_x + (radius - tick_length) * cos(radian))
            inner_y = int(rect[1] + radius - (radius - tick_length) * sin(radian))
            painter.drawLine(QPoint(outer_x, outer_y), QPoint(inner_x, inner_y))

        # Drawing the ticker
        ticker_radian = self.ticker_angle * (pi / 180)
        ticker_end_x = int(center_x + radius * cos(ticker_radian))
        ticker_end_y = int(rect[1] + radius - radius * sin(ticker_radian))
        painter.drawLine(QPoint(center_x, rect[1] + radius), QPoint(ticker_end_x, ticker_end_y))

        # Arrowhead calculations
        arrowhead_length = 20  # Adjust this value as needed
        arrow_angle = 30 * (pi / 180)  # 30 degrees to radians

        # Left arrow line
        left_arrow_x = ticker_end_x + arrowhead_length * cos(ticker_radian - pi + arrow_angle)
        left_arrow_y = ticker_end_y - arrowhead_length * sin(ticker_radian - pi + arrow_angle)
        painter.drawLine(QPoint(ticker_end_x, ticker_end_y), QPoint(int(left_arrow_x), int(left_arrow_y)))

        # Right arrow line
        right_arrow_x = ticker_end_x + arrowhead_length * cos(ticker_radian - pi - arrow_angle)
        right_arrow_y = ticker_end_y - arrowhead_length * sin(ticker_radian - pi - arrow_angle)
        painter.drawLine(QPoint(ticker_end_x, ticker_end_y), QPoint(int(right_arrow_x), int(right_arrow_y)))

    def set_ticker_angle(self, angle: float) -> None:
        """
        Sets the ticker's angle and refreshes the widget.

        :param angle: The new angle for the ticker.
        :return: None
        """
        if 0 <= angle <= 180:
            self.ticker_angle = angle
            self.update()


class DistanceIndicator(QWidget):
    """
    A widget that displays the distance value.

    :param parent: The parent window for this widget. Defaults to None.
    :type parent: QMainWindow, optional
    :param distance: The initial distance value from the object. Default's to 0.
    :type distance: Float, optional
    :param optimal_range: A tuple indicating the optimal range. Defaults to (1, 2.5).
    :type optimal_range: Tuple[int, int], optional
    :param max_distance: The maximum distance value. Default's to 6.
    :type max_distance: Float, optional
    """

    def __init__(self, parent: QWidget = None, distance: float = 0, optimal_range: Tuple[int, int] = (1, 2.5),
                 max_distance: float = 6) -> None:
        super().__init__(parent)
        self.distance = distance
        self.optimal_range = optimal_range
        self.max_distance = max_distance

        # Add a label to display the distance value
        self.distance_label = QLabel(self)
        font = self.distance_label.font()
        font.setPointSize(48)  # Set font size to 48
        font.setBold(True)  # Make the font bold
        self.distance_label.setFont(font)
        self.distance_label.setAlignment(Qt.AlignCenter)
        self.distance_label.setGeometry(0, 0, 300, 100)  # Set label size

        # Update the distance label with initial value
        self.update_distance(self.distance)

    def update_distance(self, distance: float) -> None:
        """
        Updates the distance value and refreshes the display.

        :param distance: The new distance value.
        :type distance: Float
        :return: None
        """
        self.distance = distance
        # Update the label text with the distance value
        self.distance_label.setText(f"{self.distance:.2f} ")

        # Change label color to green if within optimal range, else red
        if self.optimal_range[0] <= distance <= self.optimal_range[1]:
            self.distance_label.setStyleSheet("color: green;")
        else:
            self.distance_label.setStyleSheet("color: red;")

    def set_optimal_range(self, range_tuple: Tuple[int, int]) -> None:
        """
        Sets the optimal range for the distance indicator.

        :param range_tuple: The new optimal range as a tuple of two integers.
        :type range_tuple: Tuple[int, int]
        :return: None
        """
        self.optimal_range = range_tuple
        self.update()



class PutSual(QObject):
    flag_changed = pyqtSignal(int)  # Define flag_changed signal

    def __init__(self, joystick):
        super().__init__()
        self.handle_put_sual_flag_changed = 0




class MainWindow(QMainWindow):
    """
    The main window class for the application, managing the overall layout and widgets. It integrates all custom widgets and handles their positioning and behavior.

    :param None:
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Fixed Position Example")
        self.setGeometry(0, 0, 1920, 1080)  # Main window size

        self.video_stream = VideoStream(self)
        self.video_stream.setGeometry(0, 0, 1920, 1080)

        self.manual_label = TextInstructionLabel(self, QFont(), font_size=20, text="To control arm\nmanually press B",
                                                 color="red")
        self.manual_label.setGeometry(1585, 0, 335, 125)

        self.close_label = TextInstructionLabel(self, QFont(), font_size=20, text="To close the\napp press LB",
                                                color="red")
        self.close_label.setGeometry(0, 930, 335, 150)

        self.automatic_label = TextInstructionLabel(self, QFont(), font_size=20,
                                                    text="To automatically\nplace device press A", color="red")
        self.automatic_label.setGeometry(1500, 930, 420, 150)

        self.warning_label = TextInstructionLabel(self, QFont(), font_size=20, text="To close the\napp press LB",
                                                  color="red")
        self.warning_label.setGeometry(710, 930, 500, 150)
        self.hide_warning()

        self.semiCircleWidget = SemiCircleWidget(self)
        self.distanceIndicator = DistanceIndicator(self)
        #self.putSuhal = PutSuhal(self)

        # Apply QGraphicsOpacityEffect
        self.apply_opacity(self.semiCircleWidget, opacity=0.8)
        self.apply_opacity(self.distanceIndicator, opacity=0.8)
        #self.apply_opacity(self.putSuhal, opacity=0.8)


        # Geometry setting
        self.semiCircleWidget.setGeometry(30, 30, 280, 280)
        self.distanceIndicator.setGeometry(30, 200, 300, 75)
       # self.putSuhal.setGeometry(20, 300, 300, 75)


        self.game_controller_thread = GameControllerThread()
        self.game_controller_thread.exit.connect(self.close_application)
        self.game_controller_thread.start()

    def close_application(self) -> None:
        """
        starts the closing sequence after receiving a call from the controller.
        """
        self.game_controller_thread.stop()  # Stop the controller thread
        self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handles the close event for the main window. This function ensures a graceful shutdown by first stopping
        the video stream and then proceeding with the default close event handling.

        :param event: The close event.
        :type event: QCloseEvent
        :return: None
        """
        self.video_stream.closeEvent(event)

        super().closeEvent(event)

    def show_warning(self, text: str = "Error") -> None:
        """
        Shows a warning in accordance to the passed text. defaults to showing an error if no text it passed.

        :param text: the text which will be shown.
        :type text: str
        """
        self.warning_label.setText(text)
        self.warning_label.setVisible(True)
        self.warning_label.setGeometry(710, 930, 500, 150)

    def hide_warning(self) -> None:
        """
        Hides the currently shown warning.
        """
        self.warning_label.setVisible(False)
        self.warning_label.setGeometry(0, 0, 0, 0)

    @staticmethod
    def apply_opacity(widget: QWidget, opacity: float = 1) -> None:
        """
        Applies an opacity effect to a widget.

        :param widget: The widget to apply the opacity effect to.
        :type widget: QWidget
        :param opacity: The level of opacity to apply.
        :type opacity: Float
        :return: None
        """
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(opacity)
        widget.setGraphicsEffect(opacity_effect)


class VideoStream(QWidget):
    """
    A widget for displaying a video stream from a given RTSP URL.

    :param parent: The parent window for this widget. Defaults to None.
    :type parent: QMainWindow, optional
    :param rtsp_url: The RTSP URL to stream video from. Defaults to a sample URL.
    :type rtsp_url: str, optional
    """

    def __init__(self, parent: QMainWindow, rtsp_url: str = r"rtsp://192.168.1.18:554/video=0,audio=0") -> None:
        super(VideoStream, self).__init__(parent)
        self.rtsp_url = rtsp_url
        self.init_ui()
        self.init_frame_processor()

    def init_ui(self) -> None:
        """
        Initializes the user interface for the video stream widget, setting up layout and label for video display.

        :return: None
        """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.label = QLabel('Waiting for video stream...')
        font = QFont()
        font.setPointSize(40)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def init_frame_processor(self) -> None:
        """
        Initializes the thread for processing video frames from the RTSP stream.

        :return: None
        """

        self.frame_processor = VideoStreamThread(self.rtsp_url)
        self.frame_processor.new_frame.connect(self.update_frame)
        self.frame_processor.start()

    @pyqtSlot(QImage)
    def update_frame(self, qimg: QImage) -> None:
        """
        Updates the displayed frame with a new frame received from the video stream.

        :param qimg: The new frame to display as a QImage.
        :type qimg: QImage
        :return: None
        """
        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap.scaled(self.label.size(), aspectRatioMode=Qt.KeepAspectRatio))

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Overrides the close event for the VideoStream widget to ensure a graceful shutdown of the video stream
        and any associated resources. It stops the frame processor and waits for the video processing thread to
        terminate before closing the widget.

        :param event: The close event.
        :type event: QCloseEvent
        :return: None
        """

        if hasattr(self, 'frame_processor') and self.frame_processor is not None:
            self.frame_processor.stop()
            self.frame_processor.wait()

        super().closeEvent(event)


class VideoStreamThread(QThread):
    """
    A QThread that handles video streaming from an RTSP URL, decoding frames, and emitting them as QImages.

    :param rtsp_url: The RTSP URL to stream video from. Defaults to a sample URL.
    :type rtsp_url: str, optional
    :param running: Flag to control the running state of the thread. Defaults to True.
    :type running: bool, optional
    """
    new_frame = pyqtSignal(QImage)

    def __init__(self, rtsp_url: str = r"rtsp://192.168.1.18:554/video=0,audio=0", running: bool = True) -> None:
        super().__init__()
        self.rtsp_url = rtsp_url
        self.running = running

    def run(self) -> None:
        """
        The main execution loop of the thread that handles the video streaming.

        Opens the RTSP stream using the provided URL, decodes video frames, and emits them as QImages. This loop
        continues until the running flag is set to False, indicating the thread should stop. Proper exception
        handling and resource management ensure the video stream is closed correctly, preventing resource leaks
        and ensuring clean thread termination.

        :return: None
        """
        self.running = True
        try:
            self.container = av.open(self.rtsp_url)
            for packet in self.container.demux(video=0):
                if not self.running:
                    break
                for frame in packet.decode():
                    img = frame.to_rgb().to_ndarray()
                    qimg = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
                    self.new_frame.emit(qimg)

            self.container.close()  # Ensure the container is closed

        except Exception as e:
            print(f"Exception caught: {e}")
            self.container.close()
            time.sleep(0.5)
            self.run()

    def stop(self) -> None:
        """
        Stops the video stream processing loop.

        :return: None
        """
        self.running = False


class GameControllerThread(QThread):

    exit = pyqtSignal()
    def __init__(self) -> None:
        super(GameControllerThread, self).__init__()
        pygame.init()
        pygame.joystick.init()
        self.running = True
        self.lb_pressed_time = None
        self.axis_4_pressed = False
        self.axis_5_pressed = False
        self.axis_4_timer = QTimer(self)
        self.axis_5_timer = QTimer(self)
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.put_sual = PutSual(self.joystick)
        self.put_sual.flag_changed.connect(self.handle_put_sual_flag_changed)  # Connect to flag_changed signal
    def run(self) -> None:
        """
        The main function of the object. It runs repeatedly scanning for inputs from the controller,
        handling the closing request, and initiating the request sequence to the arm.

        :return: None
        """
        while self.running:
            for event in pygame.event.get():  # Process input events
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 4:  # LB button on a 360 controller
                        self.lb_pressed_time = time.time()  # Record the time LB was pressed
                        window.show_warning("To confirm, press RB")
                        print("AAAA")
                    elif event.button == 5 and self.lb_pressed_time:  # RB button pressed after LB
                        if time.time() - self.lb_pressed_time <= 5:  # Check if RB was pressed within 5 seconds
                            self.exit.emit()
                        self.lb_pressed_time = None  # Reset the timer after RB is pressed or the time limit expires
                    elif event.type == pygame.JOYAXISMOTION:
                        if event.axis == 4:  # Axis 0 (usually the left joystick X-axis)
                            print("Axis 0 (left joystick X-axis) motion detected")
                        if event.axis == 5:  # Axis 0 (usually the left joystick X-axis)
                            print("Axis 0 (left joystick X-axis) motion detected")

            pygame.time.wait(100)  # Wait a bit to not overload the CPU

    def handle_put_sual_flag_changed(self, new_flag):
        """
        Slot to handle the change in the flag of PutSual.
        """
        print("PutSual flag changed to:", new_flag)


    def stop(self) -> None:
        """
        stops the main function of the class and closes pyqt
        """
        self.running = False
        self.joystick.quit()
        pygame.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec_())