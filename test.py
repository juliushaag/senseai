import time
from senseai.sense import SensorManager
from senseai.sensors.camera_azure import AzureCamera
from senseai.sensors.camera_depthai import DepthAICamera
from senseai.sensors.camera_realsense import RealsenseCamera
from senseai.services.default import VisualService

man = SensorManager()

res = (512, 512)

adevs = AzureCamera.available()
ddevs = DepthAICamera.available()
rdevs = RealsenseCamera.available()

print(f"""
Found: 
  {len(adevs)} azure camera devices
  {len(ddevs)} depthai camera devices
  {len(rdevs)} depthai camera devices  
""")


# devs = [AzureCamera(dev, res) for dev in adevs]

# man.attach_sensors(*devs)
# man.wait_init()

# print("azure initialized")

# devs = [DepthAICamera(dev, res) for dev in ddevs]


man.attach_sensors(*[RealsenseCamera(dev, (640, 480)) for dev in rdevs])
man.attach_services(VisualService(man))

man.wait_init()
print("Everything is initialized")


try:
  while man.running:
    time.sleep(.1)
    man.check()
except KeyboardInterrupt:
  ...

man.shutdown()