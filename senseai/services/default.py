from senseai.sense import SensorManager
from senseai.service import ServiceTask
import cv2 as cv
import numpy as np

class VisualService(ServiceTask):

  def __init__(self, manager : SensorManager, img_size=None):
    super().__init__()
    self.man = manager
    self.img_size = img_size

  def start(self):
    self.windows = set()

  def update(self):
    data = self.man.data()
    
    values = [value for value in data.values()]


    height = max(val.shape[0] for val in values) if self.img_size is None else self.img_size[0]
    width = max(val.shape[1] for val in values) if self.img_size is None else self.img_size[1]

    # Resize all images to the same size if necessary
    images = [cv.resize(img, (width, height)) for img in values]
    
    # Define the grid dimensions
    rows = int(len(data) ** 0.5)
    cols = rows + len(data) % rows 

    # Create a blank image to hold the grid
    grid_height = height * rows
    grid_width = width * cols
    grid = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)
    grid.fill(255)  # Fill with white background

    # Place each image in the grid
    for i, img in enumerate(images):
        row = i // cols
        col = i % cols
        x = col * width
        y = row * height
        grid[y:y+height, x:x+width, :] = img

    # Display the grid
    cv.imshow('Image Grid', grid)
          
    key = cv.waitKey(20) & 0xFF
    if key == ord('q') or cv.getWindowProperty('Image Grid', cv.WND_PROP_VISIBLE) < 1:
      self.running = False
      self.man.close()

  def stop(self):
    cv.destroyAllWindows()
