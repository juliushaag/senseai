from abc import abstractmethod, ABC
from collections import deque
from threading import Thread
from typing import List




class Task(ABC):

  def __init__(self) -> None:
    super().__init__()
    self.thread : Thread = Thread(target=self._loop_impl)
    self.exceptions : deque = deque()
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

  def _loop_impl(self):
    
    self._finished = False

    self.start()

    try:
      while self._running:
        self.update()
    except Exception as e:
      self.exceptions.append(e)
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
    
    if task._running:
      self.shutdown_task(Task)

    task._running = True

    task.exceptions.clear()
    task.thread.start()

    self._tasks.append(task)

  def shutdown_task(self, task : Task):

    while task.exceptions:
      raise task.exceptions.pop()
    
    if task.thread != None:
      task._running = False
      task.thread.join()
      task.thread = None
    
    self._tasks.remove(task)
  
  def check_status(self):
    for task in self._tasks:
      if task.exceptions:
        self.shutdown()
      if task._finished:
        self.shutdown_task(task)
  
  def shutdown(self):

    for task in list(self._tasks):
      self.shutdown_task(task)
