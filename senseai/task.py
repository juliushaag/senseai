from abc import abstractmethod, ABC
from collections import deque
from threading import Thread
from typing import List




class Task(ABC):

  def __init__(self) -> None:
    super().__init__()
    self.thread : Thread = Thread(target=self._loop_impl)
    self.exceptions : deque = deque()
    self.running : bool = False
    self.finished : bool = False


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
    
    self.finished = False

    self.start()

    try:
      while self.running:
        self.update()
    except Exception as e:
      self.exceptions.append(e)
    finally:
      self.stop()
      self.finished = True

class TaskManager:

  def __init__(self) -> None:
    self._tasks : List[Task] = list()

  @property
  def tasks(self):
    return list(self._tasks)

  def start_task(self, task : Task):

    if task.running:
      self.shutdown_task(task)

    task.running = True

    task.exceptions.clear()
    task.thread.start()

    self._tasks.append(task)

  def shutdown_task(self, task : Task):

    while task.exceptions:
      raise task.exceptions.pop()
    
    if task.thread.is_alive():
      task.running = False
      task.thread.join()

    self._tasks.remove(task)
  
  def check_status(self):
    for task in self._tasks:
      if task.exceptions:
        self.shutdown()
      if task.finished:
        self.shutdown_task(task)
  
  def shutdown(self):

    for task in self._tasks:
      task.running = False
    
    for task in list(self._tasks):
      self.shutdown_task(task)
