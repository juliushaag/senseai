import time
from senseai.sense import SensorManager
from senseai.sensors.camera import OpenCVCameraSensor

from senseai.service import ServiceTask
from senseai.services.default import VisualService

import torch
from train import DEVICE, MNISTNet
import cv2 as cv

model = MNISTNet()
model.load_state_dict(torch.load("model.pt", map_location=DEVICE, weights_only=False).state_dict())

man = SensorManager()
man.attach_sensors([OpenCVCameraSensor("res/test_video.mp4")])


class MNISTService(ServiceTask):

  def __init__(self) -> None:
    super().__init__(update_freq=20)

  def start(self):
    ...

  
  def stop(self):
    ...

  
  def update(self):
    super().update()
    
    img = man.data()["OpenCVCameraSensor:0"].copy()

    img  = cv.resize(img, (28, 28), interpolation=cv.INTER_AREA)

    img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_RGB2GRAY)

    X = torch.tensor(img_gray, device=DEVICE).float().unsqueeze(0).unsqueeze(0).to(DEVICE)
    Y = model(X).argmax(dim=1, keepdim=True)
    print(Y)

man.attach_services([VisualService(man), MNISTService()])

while man.running:
  time.sleep(.1)
  man.check()

man.shutdown()