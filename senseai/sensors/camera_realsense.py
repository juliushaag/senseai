import logging
import time

import cv2
import numpy as np
import pyrealsense2 as rs
from senseai.sensors.camera import Camera

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealsenseCamera(Camera):

    CTX = rs.context()

    def __init__(self, dev : str, res : tuple[int]):
        super().__init__(resolution=res)
        
        assert dev in self.available(), f'No realsense device found matching the id {dev}'
        
        self.resolution = res
        self.dev = dev

    @classmethod
    def available(cls):
        return [dev.get_info(rs.camera_info.serial_number) for dev in RealsenseCamera.CTX.query_devices()]
    
    def open(self):
        self.pipeline = rs.pipeline(RealsenseCamera.CTX)
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, self.fps)
        self.pipeline.start(config)
        self.align = rs.align(rs.stream.color)
        
    def read(self):
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        rgb_frame = aligned_frames.get_color_frame()

        rgb_img = np.asanyarray(rgb_frame.get_data())
        return rgb_img


    def close(self):
        self.pipeline.stop()


if __name__ == "__main__":
    cam = Realsense(name="1")
    cam.connect()

    for i in range(100):
        img = cam.get_sensors()
        rgb = img["rgb"]
        # depth = img["depth"]
        # rgb = cv2.resize(img["rgb"], (256, 256))
        # depth = cv2.resize(img["depth"], (256, 256))
        cv2.imshow("rgb", rgb)
        # cv2.imshow("depth", depth)
        cv2.waitKey(1)
        time.sleep(0.1)

    cam.close()
