from enum import Flag, auto
from pathlib import Path
from typing import Tuple

import numpy as np
from senseai.sensor import SensorDevice
import cv2 as cv 


import depthai as dai

class CameraMode(Flag):
  MONO = auto(),
  STEREO = auto()
  DEPTH = auto(),
  RGB = auto()



class Camera(SensorDevice):
  def __init__(self, device_name=None) -> None:
    super().__init__(device_name)


class DepthAICamera(Camera):

  def __init__(self, mxid  : str, resolution : tuple[int]):
    super().__init__()

    resolution = tuple(reversed(resolution))

    assert mxid in DepthAICamera.available_devices(), f"The supplied depthai mxid {mxid} does not match a connected camera"

    self.pipeline = dai.Pipeline()
    self.device_info = dai.DeviceInfo(mxid)
    print("Setting up", self.device_info)

    self.fps=30
    self.resolution = resolution


  def available_devices():
    return [dev.mxid for dev in dai.Device.getAllAvailableDevices()]


  def open(self):


    # sets up the camera device, we are using a seperate pipeline for every camera
    # INFO: currently there is no reason to not just use one pipeline, but for now we keep it simple
    self.cam = self.pipeline.create(dai.node.ColorCamera)
    self.cam.setBoardSocket(dai.CameraBoardSocket.CAM_A) # A cam is stereo rgb, b and c mono probably depth
    self.cam.setPreviewSize(*tuple(reversed(self.resolution)))

    # XLinkOut: Cam to PC, XLinkIn: PC to Cam
    # We set this up to send the image from the cam to the pc 
    self.stream_name = self.device_name + "-stream"
    self.stream = self.pipeline.create(dai.node.XLinkOut)
    self.stream.setStreamName(self.stream_name)

    # link camera output to stream
    self.cam.preview.link(self.stream.input)


    self.device = dai.Device(pipeline=self.pipeline, devInfo=self.device_info, usb2Mode=False)
    self.output_queue : dai.DataOutputQueue = self.device.getOutputQueue(name=self.stream_name, maxSize=1)
    

  def close(self):
    self.output_queue.close()

    self.pipeline.remove(self.stream)
    self.pipeline.remove(self.cam)

  def get_data_shape(self) -> Tuple:
    return (*self.resolution, 3) 
  
  def get_data_type(self) -> int:
    return np.uint8

  def get_update_freq(self) -> int:
    return self.fps

  def read(self) -> Tuple[bool, np.ndarray]:
    frame = self.output_queue.get()

    if frame is not None:
      frame = frame.getCvFrame()

    return frame

class OpenCVCameraSensor(Camera):

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

