from senseai.sense import SensorManager
from senseai.service import ServiceTask

class VisualService(ServiceTask):

  def __init__(self, manager : SensorManager):
    super().__init__()
    self.man = manager
    import cv2
    self.cv = cv2

  def start(self):
    self.windows = set()

  def stop(self):
    for win in self.windows: 
      self.cv.destroyWindow(win)

  def update(self):
    data = self.man.data()
    for key in data:
      if key not in self.windows:
        self.cv.namedWindow(key)
        self.windows.add(key)


    for key, value in data.items():
      self.cv.imshow(key, value)

    key = self.cv.waitKey(20) & 0xFF
    if key == ord('q'):
      self.man.close()