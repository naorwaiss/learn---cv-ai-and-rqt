#include <librealsense2/rs.hpp> // Include RealSense Cross Platform API
#include <opencv2/opencv.hpp>   // Include OpenCV API

int main() {
    // Declare RealSense pipeline, encapsulating the actual device and sensors
    rs2::pipeline pipe;

    // Start streaming with default configuration
    pipe.start();

    while (true) {
        // Wait for the next set of frames from the camera
        rs2::frameset frames = pipe.wait_for_frames();

        // Get color frame
        rs2::frame color_frame = frames.get_color_frame();

        // Convert the RealSense frame to OpenCV matrix format
        cv::Mat color_mat(cv::Size(color_frame.as<rs2::video_frame>().get_width(),
                                   color_frame.as<rs2::video_frame>().get_height()),
                          CV_8UC3, (void*)color_frame.get_data(), cv::Mat::AUTO_STEP);

        // Display the OpenCV matrix (image)
        cv::imshow("Color Image", color_mat);

        // Check for 'q' key press to exit the loop
        if (cv::waitKey(1) == 'q')
            break;
    }

    return 0;
}
