from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from typing import Callable, Dict, Iterable, Iterator, List, Tuple
import weakref
from .sensor import SensorDevice
from .buffer import BufferDevice, BufferManager
from .service import Service, ServiceManager


class SensorManager:

  _instance = None

  def __init__(self) -> None:
    # Cleanup in every 
    if SensorManager._instance is not None:
      return RuntimeError("Multiple instancation of Sensormanager use Get()")
    
    SensorManager._instance = self 

    self._weak_ref = weakref.finalize(self, self.shutdown)
    
    self._buffer_manager = BufferManager()
    self._service_manager = ServiceManager()

    self.running = True
    self.cleaned_up = False

    self.buffer_lock = Lock()

  @staticmethod
  def Get() -> "SensorManager":
    return SensorManager._instance
    
  def attach_sensors(self, sensors : Iterable[SensorDevice]):
    self._buffer_manager.attach([BufferDevice(dev) for dev in sensors])

  def attach_services(self, services : Iterable[Service]):
    self._service_manager.attach(services)

  def shutdown(self):
    if self.cleaned_up: return

    self._service_manager._shutdown()
    self._buffer_manager.shutdown()

    self.cleaned_up = True

  def reset(self):
    with self.buffer_lock:
      self._buffer_manager.reset()

  
  def close(self):
    self.running = False

  def run(self):
    while self.running and self._service_manager.check_status() and self._buffer_manager.check_status(): 
      ...
    
    self.shutdown()
    self._service_manager.raise_errors()
    self._buffer_manager.raise_errors()

  def get_data(self, devices : Iterable[str] = None):
    self._service_manager.check_status()
    with self.buffer_lock:
      return self._buffer_manager.get_data(devices)
  

SensorManager()