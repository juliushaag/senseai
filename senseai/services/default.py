from senseai.sense import SensorManager
from senseai.service import Service
import cv2 as cv
from PyQt5.QtCore import QThread, pyqtSignal

class VisualService(Service):

  def start(self):
    self.manager = SensorManager.Get()
    self.windows = set()
  
  def stop(self):
    for win in self.windows: 
      cv.destroyWindow(win)
  
  def update(self):
    data = self.manager.get_data()
    for key in data:
      if key not in self.windows:
        cv.namedWindow(key)
        self.windows.add(key)


    for key, value in data.items():
      cv.imshow(key, value)

    key = cv.waitKey(1) & 0xFF
    if key == ord('q'):
      self.manager.close()
    if key == ord('w'):
      self.manager.reset()