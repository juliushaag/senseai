import cv2
import numpy as np
import pykinect_azure as pykinect
import logging
from typing import Optional
import time

from senseai.sensors.camera import Camera

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


pykinect.initialize_libraries()

class AzureCamera(Camera):

    RESOLUTIONS = [
      (pykinect.K4A_COLOR_RESOLUTION_720P, (1280, 720)),
      (pykinect.K4A_COLOR_RESOLUTION_1080P, (1920, 1080)),
      (pykinect.K4A_COLOR_RESOLUTION_1440P, (2560, 1440)),
      (pykinect.K4A_COLOR_RESOLUTION_1536P, (2048, 1536)),
      (pykinect.K4A_COLOR_RESOLUTION_2160P, (3840, 2160)),
    ]

    @classmethod
    def available(cls):
        return list(range(pykinect.Device.device_get_installed_count()))


    def __init__(self, device_id: int, resolution : tuple[int]):
        super().__init__(resolution=resolution, channels=3)
    
        self.resolution = resolution

        self.device_id = device_id
        self.device_config = pykinect.default_configuration
        self.device_config.color_format = pykinect.K4A_IMAGE_FORMAT_COLOR_BGRA32

        cam_conf = None
        for conf, res in AzureCamera.RESOLUTIONS:
            if res[0] > self.resolution[0] and res[1] > self.resolution[1]:
                cam_conf = conf

        assert cam_conf is not None, f"resolution {resolution} to large for {self.device_name}"
        self.device_config.color_resolution = cam_conf

        self.fps = self.device_config.camera_fps


    def open(self):
        self.device = pykinect.start_device(device_index=self.device_id, config=self.device_config)
        while not self.device.is_capture_initialized():
            self.device.update()

    def read(self) -> np.ndarray:
        capture = self.device.update()
        success, image = capture.get_color_image()
        if success: image = cv2.resize(image, self.resolution, interpolation=cv2.INTER_CUBIC)[:, :, 2::-1]
        return image

    def close(self):
        self.device.close()
