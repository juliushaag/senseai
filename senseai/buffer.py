
import asyncio
from collections import deque
from threading import Thread
import time
from typing import Dict, Iterable, Iterator, List
import abc
import numpy as np
from .sensor import SensorDevice

class BufferDevice():

  def __init__(self, dev : SensorDevice):
    self.dev = dev
    self.dev_name = dev.get_name()

  async def open(self, exception_queue : deque) -> None:
    try:
      await self.dev.open()
      self.iteration_time = 1 / self.dev.get_update_freq()
      self.data : np.ndarray = np.zeros(shape=self.dev.get_data_shape(), dtype=self.dev.get_data_type())  
    except Exception as e:
      exception_queue.append(e)


  async def close(self):
    await self.dev.close()

  def get_data(self) -> np.ndarray:
    view = self.data.view()
    view.flags.writeable = False
    return view 
  
  async def update(self, queue : deque):
    while True:
      start = time.monotonic()
      try: 
        success, value = await self.dev.read()
      except Exception as e:
        queue.append(e)
      if success:
        self.data[:] = value
      duration = time.monotonic() - start
      await asyncio.sleep(self.iteration_time - duration)
      
  def __repr__(self):
    return f"<BufferDevice dev=\"{self.dev_name}\">"
  
class BufferManager():
  
  def __init__(self) -> None:
    self._buffers : List[BufferDevice] = list() 

    self._buffer_loop = asyncio.new_event_loop()
    self._buffer_thread = Thread(target=self.buffer_thread)
    self._buffer_thread.start()

    self._exception_queue = deque()

  def get_devices(self) -> List[BufferDevice]:
    return list(self._buffers)

  def attach(self, buffers : Iterable[BufferDevice]): 
    
    for buff in buffers:
      asyncio.run_coroutine_threadsafe(buff.open(self._exception_queue), self._buffer_loop).result(), 
      self._buffer_loop.call_soon_threadsafe(
        lambda b=buff: self._buffer_loop.create_task(b.update(self._exception_queue), name=f"{b.dev_name}-loop")
      )
    
    self._buffers.extend(buffers)
    
  def shutdown(self):

    while pending := asyncio.all_tasks(self._buffer_loop):
      for task in pending: 
        self._buffer_loop.call_soon_threadsafe(task.cancel)

    self._buffer_loop.call_soon_threadsafe(self._buffer_loop.stop)
    self._buffer_thread.join()
    self._buffers.clear()

  def check_status(self):
    return len(self._exception_queue) == 0
  
  def reset(self):
    buffers = list(self._buffers)
    self.shutdown()
    self._buffer_thread = Thread(target=self.buffer_thread)
    self._buffer_thread.start()
    self.attach(buffers)


  def raise_errors(self):
    for error in self._exception_queue:
      raise error
  
  def buffer_thread(self):
    asyncio.set_event_loop(self._buffer_loop)
    self._buffer_loop.run_forever()
    self._buffer_loop.run_until_complete(asyncio.gather(*[buff.close() for buff in self._buffers])) 
    
  def get_data(self, devices : Iterable[str]):
    if devices:
      return { buff.dev_name: buff.data for buff in self._buffers if buff.dev_name in devices}
    return { buff.dev_name: buff.data for buff in self._buffers }