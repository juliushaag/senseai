from typing import Iterable, List
import weakref
from senseai.sensor import SensorDevice
from senseai.buffer import BufferTask
from senseai.service import ServiceTask

from senseai.task import TaskManager

class SensorManager:

  def __init__(self) -> None:
    
    self._weak_ref = weakref.finalize(self, self.shutdown)

    self._task_manager = TaskManager()
    self.running = True
    self.cleaned_up = False

    self._buffers : List[BufferTask] = list()
    self._services : List[ServiceTask] = list()

  def attach_sensors(self, *sensors : list[SensorDevice]):
    for dev in sensors:
      task = BufferTask(dev)
      self._task_manager.start_task(task)
      self._buffers.append(task)

  def attach_services(self, *services : list[ServiceTask]):
    for service in services: 
      self._task_manager.start_task(service)
      self._services.append(service)

  def shutdown(self):
    if self.cleaned_up: return
    self._task_manager.shutdown()
    self.cleaned_up = True

  def reset(self):

    self._task_manager.shutdown()

    for task in self._buffers:
      self._task_manager.start_task(task)

    for service in self._services:
      self._task_manager.start_task(service)


  def close(self):
    self.running = False
    
  def check(self):
    self._task_manager.check_status()
    if not self.running:
      self.shutdown()

  def data(self, devices : Iterable[str] = None):
    if not devices:
      return { buff.dev_name : buff.data for buff in self._buffers }
    else:
      return { buff.dev_name : buff.data for buff in self._buffers if buff.dev_name in devices }
    

  def wait_init(self):
    while not all(buff.initialized or buff.finished for buff in self._buffers):
      ...

  def __del__(self):
    self._task_manager.shutdown()