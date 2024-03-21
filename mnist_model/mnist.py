import torch
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda
import torch
from torch.utils.data import Dataset
from json import JSONEncoder
import json

from torchvision import transforms
from PIL import Image
import numpy as np
import sys

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python mnist.py numClients clientIndex")
        sys.exit(1)

    # Retrieve the arguments
    numClients = int(sys.argv[1])
    clientIndex = int(sys.argv[2])

    # Print the arguments
    print("Argument 1:", numClients)
    print("Argument 2:", clientIndex)
        
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

    # Define the fraction you want to use (0, 1, 2, or 3)
    chosen_fraction = clientIndex  # Change this to select a different fraction (0-indexed)

    # Assuming len(training_data) and len(test_data) are known
    fraction_train_length = len(training_data) // numClients
    fraction_test_length = len(test_data) // numClients

    start_index_train = chosen_fraction * fraction_train_length
    end_index_train = (chosen_fraction + 1) * fraction_train_length

    start_index_test = chosen_fraction * fraction_test_length
    end_index_test = (chosen_fraction + 1) * fraction_test_length

    # Create subsets for the chosen fraction of the datasets
    train_subset = Subset(training_data, range(start_index_train, end_index_train))
    test_subset = Subset(test_data, range(start_index_test, end_index_test))

    # Create data loaders for the subsets
    train_dataloader = DataLoader(train_subset, batch_size=64)
    test_dataloader = DataLoader(test_subset, batch_size=64)

    # train_dataloader = DataLoader (training_data, batch_size = 64)
    # test_dataloader = DataLoader(test_data, batch_size = 64)

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

    lr = 1e-3
    bs = 64
    epochs = 10

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

    for t in range(5):
        train_data(model)
        test_data(model)

    #for param in model.parameters():
    #    print(param)
    #    print(len(param))

    for param_tensor in model.state_dict():
        print(param_tensor, "\t", model.state_dict()[param_tensor].size())
    #    print(param_tensor, "\t", model.state_dict()[param_tensor])

    ### Standard serialized save
    #torch.save(model.state_dict(), './state/model.pth')

    class EncodeTensor(JSONEncoder,Dataset):
        def default(self, obj):
            if isinstance(obj, torch.Tensor):
                return obj.cpu().detach().numpy().tolist()
            return super(EncodeTensor, self).default(obj)

    #with open('torch_weights.json', 'w') as json_file:
    #    json.dump(model.state_dict(), json_file,cls=EncodeTensor)

    for count, param_tensor in enumerate(model.state_dict()):
        with open('../mnist_model/weights/torch_weights'+str(count)+'.json', 'w') as json_file:
            json.dump(model.state_dict()[param_tensor], json_file,cls=EncodeTensor)
