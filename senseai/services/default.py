from senseai.sense import SensorManager
from senseai.service import ServiceTask
import cv2 as cv

class VisualService(ServiceTask):

  def __init__(self, manager : SensorManager):
    super().__init__()
    self.man = manager

  def start(self):
    self.windows = set()

  def stop(self):
    for win in self.windows: 
      cv.destroyWindow(win)

  def update(self):
    data = self.man.data()
    for key in data:
      if key not in self.windows:
        cv.namedWindow(key)
        self.windows.add(key)


    for key, value in data.items():
      cv.imshow(key, value)
      
    key = cv.waitKey(20) & 0xFF
    if key == ord('q'):
      self.man.close()