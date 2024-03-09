import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda
import json
import ast

from torchvision import transforms
from PIL import Image
import numpy as np

### Grabbing MNIST data with torchvision datasets
training_data = datasets.MNIST(
   root = 'data',
   train = True,
   download = True,
   transform = ToTensor()
)
test_data = datasets.MNIST(
   root = 'data',
   train = False,
   download = True,
   transform = ToTensor()
)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
#print(device)
#print(torch.cuda.device_count())
#print(torch.cuda.current_device())
#print(torch.cuda.device(0))
#print(torch.cuda.get_device_name(0))

training_data[0][0].shape
training_data[0][0].squeeze().shape
training_data = list(map(list, training_data))
test_data = list(map(list, test_data))

for count in range(len(training_data)):

    # Convert the PyTorch tensor to a PIL Image
    pil_image = transforms.ToPILImage()(training_data[count][0])

    # Resize the image to 16x16
    resized_image = pil_image.resize((12, 12))

    # Convert the resized image back to a PyTorch tensor
    training_data[count][0] = transforms.ToTensor()(resized_image)

for count in range(len(test_data)):
    
    # Convert the PyTorch tensor to a PIL Image
    pil_image = transforms.ToPILImage()(test_data[count][0])

    # Resize the image to 16x16
    resized_image = pil_image.resize((12, 12))

    # Convert the resized image back to a PyTorch tensor
    test_data[count][0] = transforms.ToTensor()(resized_image)
    
train_dataloader = DataLoader (training_data, batch_size = 64)
test_dataloader = DataLoader(test_data, batch_size = 64)

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(12*12, 32),
            nn.ReLU(),
            nn.Linear(32, 10)
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

model = NeuralNetwork().to(device)
#model = NeuralNetwork().to('cpu')

state_dict = model.state_dict()

keys_list = ['linear_relu_stack.0.weight', 'linear_relu_stack.0.bias', 'linear_relu_stack.2.weight', 'linear_relu_stack.2.bias']

for count in range(len(keys_list)):
    with open('~/CS277/mnist_model/aggregate/plain_weights'+str(count)+'.json', 'r') as json_file:
        state_dict[keys_list[count]] = torch.Tensor(ast.literal_eval(json_file.read()))

#for count in range(len(keys_list)):
#    with open('./aggregate/ckks_weights'+str(count)+'.json', 'r') as json_file:
#       state_dict[keys_list[count]] = torch.Tensor(ast.literal_eval(json_file.read()))

model.load_state_dict(state_dict)

lr = 1e-3
bs = 64
epochs = 5

loss_fn = nn.CrossEntropyLoss()

optimizer = torch.optim.SGD(model.parameters(), lr=lr)

def train_data(model):
    for xb, yb in train_dataloader:
        xb = xb.clone().detach().to(device)
        yb = yb.clone().detach().to(device)
        preds = model(xb)
        loss = loss_fn(preds, yb)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    loss = loss.item()
    print(f"Train loss: {loss:>7f}")

def test_data(model):
    num_batches = len(test_dataloader)
    size = len(test_dataloader.dataset)
    test_loss, corrects = 0, 0

    with torch.no_grad():
        for xb, yb in test_dataloader:
            xb = xb.clone().detach().to(device)
            yb = yb.clone().detach().to(device)
            preds = model(xb)
            test_loss += loss_fn(preds, yb).item()
            corrects += (preds.argmax(1) == yb).type(torch.float).sum().item()

    test_loss /= num_batches
    # test_loss = lo
    corrects /= size
    print(f"Test loss: \n Accuracy: {(100*corrects):>0.1f}%, Avg loss: {test_loss:>8f} \n")

for t in range(4):
    train_data(model)
    test_data(model)

#torch.save(model.state_dict(), './state/model.pth')
