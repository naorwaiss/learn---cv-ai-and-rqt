import torch
from torch import nn
import torchvision
from torchvision import datasets, transforms
from torchvision.transforms import ToTensor
import matplotlib.pyplot as plt

print(torch.__version__)
print(torchvision.__version__)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"the sion of the cuda is: {torch.version.cuda} and we use the cuda device: {device}")

# Setup train data
# Get the basic dataset from PyTorch
train_data = datasets.FashionMNIST(root="data", train=True, download=True, transform=torchvision.transforms.ToTensor(), target_transform=None)

test_data = datasets.FashionMNIST(root="data", train=True, download=True, transform=torchvision.transforms.ToTensor(), target_transform=None)

class_names = train_data.class_to_idx

print("Class Names:", class_names)

image, label = train_data[0]
print(f"Image shape: {image.shape}")

plt.imshow(image.squeeze(), cmap="gray")
plt.axis('off')  # Turn off the axes
plt.show()



torch.manual_seed(42)
fig = plt.figure(figsize=(9,9))
rows,cols = 4,4
for i in  range(1,rows*cols+1):
    random_idx = torch.randint(0,len(train_data),size=[1]).item()
    print(random_idx)
    img , label = train_data[random_idx]
    fig.add_subplot()






