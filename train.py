
import torch, torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader

# Constants
BATCH_SIZE = 32
LEARNING_RATE = 1e-3
MOMENTUM = 0.8
EPOCHS = 5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class MNISTNet(nn.Module):
  def __init__(self):
    super().__init__()

    self.net = nn.Sequential(
      nn.Conv2d(1, 10, kernel_size=5),
      nn.MaxPool2d(2),
      nn.ReLU(),
      nn.Conv2d(10, 20, kernel_size=5),
      nn.MaxPool2d(3),
      nn.ReLU(),
      nn.Flatten(),
      nn.Linear(80, 50),
      nn.ReLU(),
      nn.Dropout(),
      nn.Linear(50, 10),
    )

  def forward(self, x):
    x = self.net(x)
    return F.softmax(x, dim=1)


if __name__ == "__main__":
  

  # Define transformations
  transform = transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize((0.1307,), (0.3081,)),
  ])

  # Load datasets
  train_dataset = torchvision.datasets.MNIST(root='data/', train=True, download=True, transform=transform)
  test_dataset = torchvision.datasets.MNIST(root='data/', train=False, download=True, transform=transform)

  train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
  
  network = MNISTNet().to(DEVICE)
  optimizer = optim.AdamW(network.parameters(), lr=LEARNING_RATE)

  # Main training loop
  for _ in range(0, EPOCHS):
    network.train()
    loss_summed = 0
    for data, target in train_loader:
      X, Y = data.to(DEVICE), target.to(DEVICE)   
      optimizer.zero_grad()
      y = network(X)
      loss = F.cross_entropy(y, Y)
      loss.backward()
      optimizer.step()
      loss_summed += loss.item()


    network.eval()
    with torch.no_grad():
      y = network(test_dataset.data.float().unsqueeze(1))
      test_loss = F.cross_entropy(y, test_dataset.targets).item()
      Y = test_dataset.targets
      pred = y.argmax(dim=1, keepdim=True)
      correct = (pred.flatten() == Y).sum().item()

      print(f'train loss: {loss_summed / len(train_loader):.4f}, '
            f'test loss: {test_loss:.4f}, '
            f'Accuracy: {correct}/{len(test_dataset)} '
            f'({100. * correct / len(test_dataset):.2f}%)')


  # save model
  torch.save(network, "model.pt")