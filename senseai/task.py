from abc import abstractmethod, ABC
from collections import deque
from threading import Thread
from typing import List

class Task(ABC):

  def __init__(self) -> None:
    super().__init__()
    self._thread : Thread = None
    self._exceptions : deque = None
    self._running : bool = False

    self._finished : bool = False


  @abstractmethod
  def start():
    ...

  @abstractmethod
  def stop():
    ...

  @abstractmethod  
  def update():
    ...

  def _thread_loop_impl(self):
    
    self._finished = False

    self.start()

    try:
      while self._running:
        self.update()
    except Exception as e:
      self._exceptions.append(e)
    finally:
      self.stop()
    
    self._finished = True

class TaskManager:

  def __init__(self) -> None:
    self._tasks : List[Task] = list()

  @property
  def tasks(self):
    return list(self._tasks)

  def start_task(self, task : Task):
    
    if task._thread != None:
      self.shutdown_task(Task)

    task._thread = Thread(target=task._thread_loop_impl)
    task._running = True
    task._exceptions = deque()
    task._thread.start()

    self._tasks.append(task)

  def shutdown_task(self, task : Task):

    while task._exceptions:
      raise task._exceptions.pop()
    
    if task._thread != None:
      task._running = False
      task._thread.join()
      task._thread = None
    
    if task in self._tasks: self._tasks.remove(task)
  
  def check_status(self):
    for task in self._tasks:
      if len(task._exceptions) > 0:
        self.shutdown()
      if task._finished:
        self.shutdown_task(task)
  
  def shutdown(self):

    for task in list(self._tasks):
      self.shutdown_task(task)
