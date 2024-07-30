from senseai.sense import SensorManager
from senseai.sensors.camera import OpenCVCameraSensor
import cv2 as cv
from senseai.service import Service
from senseai.services.default import VisualService

import torch, torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader

# Constants
BATCH_SIZE = 128
LEARNING_RATE = 0.01
MOMENTUM = 0.9
EPOCHS = 10
DEVICE = "cpu"


# Define transformations
transform = transforms.Compose([
    transforms.ToTensor(),
    # transforms.Normalize((0.1307,), (0.3081,))
])

# Load datasets
train_dataset = torchvision.datasets.MNIST(root='data/', train=True, download=True, transform=transform)
test_dataset = torchvision.datasets.MNIST(root='data/', train=False, download=True, transform=transform)

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=128, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=128, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class MNISTNet(nn.Module):
  def __init__(self):
    super(MNISTNet, self).__init__()
    self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
    self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
    self.fc1 = nn.Linear(320, 50)
    self.fc2 = nn.Linear(50, 10)

  def forward(self, x):
    x = F.relu(F.max_pool2d(self.conv1(x), 2))
    x = F.relu(F.max_pool2d(self.conv2(x), 2))
    x = x.view(-1, 320)
    x = F.relu(self.fc1(x))
    x = F.dropout(x, training=self.training)
    x = self.fc2(x)
    return F.log_softmax(x, dim=1)


network = MNISTNet().to(device)
optimizer = optim.SGD(network.parameters(), lr=0.1, momentum=0.9)
loss_fn = F.cross_entropy

# Training function
def train():
  network.train()
  for data, target in train_loader:
    X, Y = data.to(device), target.to(device)
    
    optimizer.zero_grad()
    y = network(X)
    loss = loss_fn(y, Y)
    loss.backward()
    optimizer.step()

# Testing function
def test():
  network.eval()
  test_loss = 0
  correct = 0
  with torch.no_grad():
    for data, target in test_loader:
      X, Y = data.to(device), target.to(device)
      
      y = network(X)
      test_loss += loss_fn(y, Y, reduction='sum').item()
      pred = y.argmax(dim=1, keepdim=True)
      correct += pred.eq(Y.view_as(pred)).sum().item()

  test_loss /= len(test_loader.dataset)
  print(f'Test set: Average loss: {test_loss:.4f}, '
        f'Accuracy: {correct}/{len(test_loader.dataset)} '
        f'({100. * correct / len(test_loader.dataset):.2f}%)')

# Main training loop
num_epochs = 2
for epoch in range(1, num_epochs + 1):
  train()
  test()


man = SensorManager.Get()
man.attach_sensors([OpenCVCameraSensor("res/test_video.mp4")])


class MNISTService(Service):

  def __init__(self) -> None:
    super().__init__(update_freq=10)

  def start(self):
    ...

  
  def stop(self):
    ...

  
  def update(self):
    img = man.get_data()["OpenCVCameraSensor:0"].copy()
    
    
    img = cv.resize(img, (28, 28), interpolation=cv.INTER_AREA)

    img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_RGB2GRAY)


    X = torch.tensor(img_gray, device="cuda").float().unsqueeze(dim=0).unsqueeze(dim=0).to(device)
    Y : torch.Tensor = network(X)
    # print(Y.var())
    if Y.var() >= 0.1:
      print(max(enumerate(*Y.tolist()), key=lambda x: x[1]))

class NeuralView(Service):

  
  def __init__(self) -> None:
    super().__init__(update_freq=20)


  def start(self):
    self.manager = SensorManager.Get()
    cv.namedWindow("Neural")
  
  def stop(self):
    cv.destroyWindow("Neural")
  
  def update(self):
    img = man.get_data()["OpenCVCameraSensor:0"].copy()

    img = cv.resize(img, (28, 28), interpolation=cv.INTER_AREA)

    img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_RGB2GRAY)
    cv.imshow("Neural", img_gray)
    
    key = cv.waitKey(1) & 0xFF
    if key == ord('q'):
      self.manager.close()
    if key == ord('w'):
      self.manager.reset()


man.attach_services([NeuralView(), MNISTService()])
man.run()
