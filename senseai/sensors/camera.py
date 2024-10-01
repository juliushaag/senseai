from pathlib import Path
from typing import Tuple

import numpy as np
from senseai.sensor import SensorDevice

import cv2 as cv 

class OpenCVCameraSensor(SensorDevice):

  def __init__(self, path : Path = None, fps = None, res = None) -> None:
    super().__init__()
    self.device = path or 0
    self.fps = fps
    self.res = res

  def open(self):
    self.cap = cv.VideoCapture(self.device)

    if self.fps is None:
      self.fps = self.cap.get(cv.CAP_PROP_FPS)

    self.width = self.res[0] if self.res else int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
    self.height = self.res[1] if self.res else int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))

  def get_data_shape(self) -> Tuple:
    return (self.height, self.width, 3)  
  
  def get_data_type(self) -> int:
    return np.uint8

  def get_update_freq(self) -> int:
    return self.fps

  def read(self) -> Tuple[bool, np.ndarray]:
    success, frame = self.cap.read()

    if self.res:
      frame = cv.resize(frame, self.res, interpolation=cv.INTER_AREA)
  
    return success, frame

  def close(self):
    self.cap.release()

