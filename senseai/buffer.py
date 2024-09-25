
import asyncio
from collections import deque
from threading import Thread
import time
from typing import Dict, Iterable, Iterator, List

import numpy as np
from senseai.sensor import SensorDevice
from senseai.task import Task
from threading import Lock

class BufferTask(Task):

  def __init__(self, dev : SensorDevice):
    super().__init__()
    self.initialized = False
    self.dev = dev

  def start(self):
    self.dev.open()

    self.dev_name = self.dev.get_name()
    self.data : np.ndarray = np.zeros(shape=self.dev.get_data_shape(), dtype=self.dev.get_data_type())  
    self.iteration_time = 1 / self.dev.get_update_freq()
    self.data_lock = Lock()

    
    self.initialized = True


  def stop(self):
    self.dev.close()

  def get_data(self) -> np.ndarray:
    with self.data_lock():
      view = self.data.view()
    view.flags.writeable = False
    return view 
  
  def update(self):
    start = time.monotonic()
    success, value = self.dev.read()
    if success:
      with self.data_lock:
        self.data[:] = value
    duration = time.monotonic() - start
    time.sleep(self.iteration_time - duration)
      
  def __repr__(self):
    return f"<BufferDevice dev=\"{self.dev_name}\">"
  