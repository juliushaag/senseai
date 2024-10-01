from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Tuple
import numpy as np


class SensorDevice(ABC):

  _SENSOR_CLASSES_COUNT = defaultdict(lambda: 0)

  def __init__(self, device_name = None) -> None:
    super().__init__()

    self.device_name = device_name
    if not self.device_name:
      cls_name = self.__class__.__name__
      self.device_name = f"{str(cls_name)}:{SensorDevice._SENSOR_CLASSES_COUNT[cls_name]}"
      SensorDevice._SENSOR_CLASSES_COUNT[cls_name] += 1 
    

  def get_name(self):
    return self.device_name
  
  @abstractmethod
  def get_update_freq(self):
    ...

  @abstractmethod
  def get_data_shape(self) -> Tuple:
    ...

  @abstractmethod
  def get_data_type(self) -> Tuple:
    ...

  @abstractmethod
  async def open(self):
    ...

  @abstractmethod
  async def close(self) -> np.ndarray:
    ...

  @abstractmethod
  async def read(self) -> Tuple[bool, np.ndarray]:
    ...


    
  
