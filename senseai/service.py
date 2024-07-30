from abc import ABC, abstractmethod
import asyncio
from collections import deque
import queue
from threading import Thread
import time
from typing import Deque, Dict, Iterable, List


class Service(ABC):

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
    
  @abstractmethod
  def update(self):
    ...


class ServiceManager:

  def __init__(self) -> None:
    
    self.services : List[Service] = list()
    self.threads : Dict[Service, Thread] = dict()

    self.exception_queue = deque()
  
  def check_status(self):
    return len(self.exception_queue) == 0
    

  def raise_errors(self):
    for error in self.exception_queue:
      raise error

  def attach(self, services : Iterable[Service]):

    for service in services:
      thread = Thread(
        target=ServiceManager._run_impl, 
        name=service.name + "-thread", 
        args = [service, self.exception_queue]
      )
      thread.start()
      self.threads[service] = thread
    
    self.services.extend(services)
    self.check_status()

  def _shutdown(self):
    
    for service, thread in self.threads.items():
      service.running = False
      thread.join()

  @staticmethod
  def _run_impl(service : Service, queue):
    try:
      service.start()
      while service.running:
        service.update()
        time.sleep(1 / service.update_freq)
    except Exception as e:
      queue.append(e)
    finally:
      service.stop()
      