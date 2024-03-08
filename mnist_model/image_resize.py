import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda
import torch
from torch.utils.data import Dataset
from json import JSONEncoder
import json

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

print(training_data[0][0].shape)
print(training_data[0][0].squeeze().shape)

# print(len(training_data[0][1]))
######################################################
# Choose a sample image from the dataset
original_tensor = training_data[0][0]

# Convert the PyTorch tensor to a PIL Image
pil_image = transforms.ToPILImage()(original_tensor)

# Resize the image to 16x16
resized_image = pil_image.resize((12, 12))

# Convert the resized image back to a PyTorch tensor
resized_tensor = transforms.ToTensor()(resized_image)

# Display the original and resized tensor shapes
print("Original tensor shape:", original_tensor.shape)
print("Resized tensor shape:", resized_tensor.shape)

# You can save the resized image if needed
resized_image.save("resized_image.png")

### Load Data
train_dataloader = DataLoader (training_data, batch_size = 64)
test_dataloader = DataLoader(test_data, batch_size = 64)
