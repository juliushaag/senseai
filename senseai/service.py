from abc import ABC, abstractmethod
from collections import deque
from threading import Thread
import time
from typing import Deque, Dict, Iterable, List
from senseai.task import Task

class ServiceTask(Task):

  def __init__(self, update_freq = 50, name = None) -> None:
    super().__init__()

    self.update_freq = update_freq
    self.name = name or self.__class__.__name__
    self.running = True


  @abstractmethod
  def start(self, manager):
    ...

  @abstractmethod
  def stop(self):
    ...
    
  def update(self):
    time.sleep(1 / self.update_freq)