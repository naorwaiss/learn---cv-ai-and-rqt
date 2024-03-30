import torch
from torch import nn
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sklearn
import pandas as pd
from sklearn.datasets import make_circles
from sklearn.model_selection import train_test_split
import requests
from pathlib import Path

torch.manual_seed(42)
torch.cuda.manual_seed(42)


#1.make some classification data

n_samples = 1000

X, y = make_circles(n_samples,noise=0.03,random_state=42)

print(f"print 5 sampole of X: \n {X[:5]}")
print(f"firs 5 sample of y : \n {y[:5]}")

circles = pd.DataFrame({"X1": X[:, 0], "X2": X[:, 1],"label": y})

#print(circles.head(10))


plt.scatter(x=X[:,0],y=X[:,1],c=y,cmap=plt.cm.RdYlBu);
plt.show()


X_sample = X[0]
y_sample = y[0]

print(f"Value for the sample of x: {X_sample} and the same for y: {y_sample}")
print(f"shapes for one sample of X: {X_sample.shape} and the same for y: {y_sample.shape}")


#turn data into tensors


X = torch.from_numpy(X).type(torch.float)
y = torch.from_numpy(y).type((torch.float))

#split data
X_train , X_test , y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)

device = "cuda" if torch.cuda.is_available() else "cpu"

print(device)


# class CircleModelV0(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.layer_1 = nn.Linear(in_features=2,out_features=5)  #take in 2 feature and make it to 5
#         self.layer_2 = nn.Linear(in_features=5,out_features=1)  # from 5 output of the firs liniar layer we make 1  feature
#
#     def forward(self, X):
#         return self.layer_2(self.layer_1(X))
#
#
# model_0 = CircleModelV0().to(device)



#nn.Sequential()

model_0 = nn.Sequential(nn.Linear(in_features=2,out_features=5),nn.Linear(in_features=5,out_features=1)).to(device)

with torch.inference_mode():
    untrained_preds = model_0(X_test.to(device))
print(f"Length of prediction: {len(untrained_preds)} , shape: {untrained_preds.shape}")
print(f"Length of test samples: {len(X_test)}, shape: {X_test.shape}")
print(f"\nFirst 10 prediction:\n {torch.round(untrained_preds[:10])}")
print(f"\nFirst 10 labels:\n {y_test[:10]}")


loss_fn = nn.BCEWithLogitsLoss()

optimizer = torch.optim.SGD(params=model_0.parameters(),lr=0.1)


#calcualte the accuricy

def accuracy_fn(y_true , y_pred):
    correct = torch.eq(y_true, y_pred).sum().item()
    acc = (correct/len(y_pred)) * 100
    return acc



#train the model
model_0.eval()
with torch.inference_mode():
    y_logits = model_0(X_test.to(device))[:5]
print(y_logits)

y_pred_probs = torch.sigmoid(y_logits)

y_preds = torch.round(y_pred_probs)
y_preds_labels = torch.round(torch.sigmoid(model_0(X_test.to(device))[:5]))

print(torch.eq(y_preds.squeeze(),y_preds_labels.squeeze())) #get red extra dim

y_preds.squeeze()



epochs = 100
X_train, y_train = X_train.to(device), y_train.to(device)
X_test , y_test = X_test.to(device), y_test.to(device)

for epoch in range(epochs):
    model_0.train()


    #forward pass
    y_logits = model_0(X_train).squeeze()
    y_preds = torch.round(torch.sigmoid(y_logits))
    #
    # loss = loss_fn(torch.sigmoid(y_logits),y_train)
    loss = loss_fn(y_logits,y_train)
    acc = accuracy_fn(y_true=y_train, y_pred=y_preds)



    optimizer.zero_grad()

    loss.backward()

    optimizer.step()


    ###testing


    model_0.eval()
    with torch.inference_mode():
        test_logits = model_0(X_test).squeeze()
        test_pred = torch.round(torch.sigmoid(test_logits))

        test_loss = loss_fn(test_logits,y_test)
        test_acc = accuracy_fn(y_true=y_test,y_pred=test_pred)


    if epoch % 10 == 0:
        print(f"Epoch: {epoch} | Loss {loss:.5f}, Acc: {acc:.2f}% | Test lossL {test_loss:.5f}, Test acc: {test_acc:.2f}%")




#from the metrix it look like the code didnt learn nothing

#download helper function

if Path("helper_function.py").is_file():
    print("helper_function.py already exists, skipping download")
else:
    print("Download helper_function.py")
    request = requests.get("https://raw.githubusercontent.com/mrdbourke/pytorch-deep-learning/main/helper_functions.py")
    with open("helper_function.py", "wb") as f:
        f.write(request.content)


from helper_function import  plot_predictions, plot_decision_boundary


plt.figure(figsize=(12, 6))
plt.subplot(1,2,1)
plt.title("Train")
plot_decision_boundary(model_0, X_train, y_train)
plt.subplot(1,2,2)
plt.title("Test")
plot_decision_boundary(model_0,X_test,y_test)

plt.show()
