import depthai as dai
import numpy as np
from senseai.sensors.camera import Camera

class DepthAICamera(Camera):

  def __init__(self, mxid  : str, resolution : tuple[int]):
    super().__init__(resolution=resolution, channels=3)

    resolution = resolution

    assert mxid in DepthAICamera.available(), f"The supplied depthai mxid {mxid} does not match a connected camera"

    self.pipeline = dai.Pipeline()
    self.device_info = dai.DeviceInfo(mxid)

    self.resolution = resolution

  @classmethod
  def available(cls):
    return [dev.mxid for dev in dai.Device.getAllAvailableDevices()]


  def open(self):
    # sets up the camera device, we are using a seperate pipeline for every camera
    # INFO: currently there is no reason to not just use one pipeline, but for now we keep it simple
    self.cam = self.pipeline.create(dai.node.ColorCamera)
    self.cam.setBoardSocket(dai.CameraBoardSocket.CAM_A) # A cam is stereo rgb, b and c mono probably depth
    self.cam.setPreviewSize(*self.resolution)

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
    self.device.close()

    self.pipeline.remove(self.stream)
    self.pipeline.remove(self.cam)


  def read(self) -> np.ndarray:
    
    frame = self.output_queue.tryGet()

    if frame is not None:
      frame = frame.getCvFrame()

    return frame