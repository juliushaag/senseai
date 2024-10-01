from enum import Flag, auto
from pathlib import Path
from typing import Tuple

import numpy as np
from senseai.sensor import SensorDevice
import cv2 as cv 
from abc import abstractmethod


class CameraMode(Flag):
  MONO = auto(),
  STEREO = auto()
  DEPTH = auto(),
  RGB = auto()



class Camera(SensorDevice):
  def __init__(self, device_name=None, resolution=(1920, 1080), channels=3,data_type=np.uint8, fps=30) -> None:
    super().__init__(device_name)

    self.data_shape = (*reversed(resolution), channels)
    self.data_type = data_type
    self.fps = fps


  @classmethod
  @abstractmethod
  def available(cls):
    ...

  def get_data_shape(self) -> Tuple:
    return self.data_shape  
  
  def get_data_type(self) -> int:
    return self.data_type

  def get_update_freq(self) -> int:
    return self.fps


class OpenCVCameraSensor(Camera):

  def __init__(self, path : Path, fps, res) -> None:
    super().__init__(resolution=res, channels=3, fps=fps)
    self.device = path or 0

  def open(self):
    self.cap = cv.VideoCapture(self.device)

    if self.fps is None:
      self.fps = self.cap.get(cv.CAP_PROP_FPS)

    self.width = self.res[0] if self.res else int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
    self.height = self.res[1] if self.res else int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))


  def read(self) -> Tuple[bool, np.ndarray]:
    success, frame = self.cap.read()

    if self.res:
      frame = cv.resize(frame, self.res, interpolation=cv.INTER_AREA)
  
    return success, frame

  def close(self):
    self.cap.release()

