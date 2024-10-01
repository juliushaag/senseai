import time
from senseai.sense import SensorManager
from senseai.sensors.camera_azure import AzureCamera
from senseai.sensors.camera_depthai import DepthAICamera
from senseai.sensors.camera_realsense import Realsense
from senseai.services.default import VisualService

man = SensorManager()

res = (512, 512)

adevs = AzureCamera.available()
ddevs = DepthAICamera.available()
rdevs = Realsense.available()
print(f"""
Found: 
  {len(adevs)} azure camera devices
  {len(ddevs)} depthai camera devices
""")


# devs = [AzureCamera(dev, res) for dev in adevs]

# man.attach_sensors(*devs)
# man.wait_init()

# print("azure initialized")

# devs = [DepthAICamera(dev, res) for dev in ddevs]


man.attach_sensors(Realsense(res))
man.attach_services(VisualService(man, img_size=(512, 512)))

man.wait_init()
print("Everything is initialized")


try:
  while man.running:
    time.sleep(.1)
    man.check()
except KeyboardInterrupt:
  ...

man.shutdown()