import time
from senseai.sense import SensorManager
from senseai.sensors.camera import OpenCVCameraSensor, DepthAICamera

from senseai.services.default import VisualService

man = SensorManager()

devs = DepthAICamera.available_devices()
ddevs = [DepthAICamera(dev, (620, 320)) for dev in devs]

man.attach_sensors(*ddevs)
man.attach_services(VisualService(man))

man.wait_init()

while man.running:
  time.sleep(.1)
  man.check()

man.shutdown()