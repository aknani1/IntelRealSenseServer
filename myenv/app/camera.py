import pyrealsense2 as rs
import numpy as np
import cv2
import base64
from app import socketio
pipeline = rs.pipeline()
config = rs.config()
def generate_frames():

    config.enable_stream(rs.stream.color, 640, 360, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
    pipeline.start(config)

    try:
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
            if not color_frame or not depth_frame:
                continue
            color_image = np.asanyarray(color_frame.get_data())
            depth_colorized = rs.colorizer().colorize(depth_frame)
            depth_image = np.asanyarray(depth_colorized.get_data())
            _, color_buffer = cv2.imencode('.jpg', color_image)
            _, depth_buffer = cv2.imencode('.jpg', depth_image)

            color_frame_encoded = base64.b64encode(color_buffer).decode('utf-8')
            depth_frame_encoded = base64.b64encode(depth_buffer).decode('utf-8')

            yield {"color": color_frame_encoded, "depth": depth_frame_encoded}
    finally:
        pipeline.stop()
