import numpy as np
import pandas as pd
from PIL import Image
import time
import os
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device = torch.device('cpu')
print(device)


def read_data(PATH, n_characters=20, im_height=105, im_with=105):
    alphabets = os.listdir(f'{PATH}')
    alphabets.sort()
    data = []
    for i_alphabet, alphabet in enumerate(alphabets):
        characters = os.listdir(f'{PATH}/{alphabet}')
        characters.sort()
        alphabet_data = np.zeros((len(characters), n_characters, im_height, im_with))
        for i_character, character in enumerate(characters):
            pictures = os.listdir(f'{PATH}/{alphabet}/{character}')
            pictures.sort()
            for i_picture, picture in enumerate(pictures):
                im = np.array(Image.open(f'{PATH}/{alphabet}/{character}/{picture}'))
                alphabet_data[i_character, i_picture] = im
        data.extend(alphabet_data)
    return np.array(data)


def transform_data(data, N_train_samples, N_characters, im_height, im_with):
    N_categories = data.shape[0]
    x = np.zeros((N_train_samples, 2, im_height, im_with))
    y = np.zeros((N_train_samples, 1))
    for i in range(int(N_train_samples / 2)):
        idx_category = np.random.choice(np.arange(N_categories), size=2, replace=False)
        idx_true = np.random.choice(np.arange(N_characters), size=2, replace=False)
        idx_false = np.random.choice(np.arange(N_characters))
        x[i * 2] = data[idx_category[0], idx_true]
        y[i * 2] = 1
        x[i * 2 + 1] = np.concatenate((data[idx_category[0], idx_true[0]][np.newaxis],
                                       data[idx_category[1], idx_false][np.newaxis]),
                                      axis=0)
        y[i * 2 + 1] = 0
    return torch.from_numpy(x).float().to(device), torch.from_numpy(y).float().to(device)


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 64, kernel_size=5)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=5)
        self.conv3 = nn.Conv2d(128, 128, kernel_size=5)
        self.fc1 = nn.Linear(128 * 9 * 9, 256)
        self.fc2 = nn.Linear(256, 4096)
        self.fc3 = nn.Linear(4096, 1)

    def forward(self, x):
        x = torch.abs(self.siamese(x[:, 0:1]) - self.siamese(x[:, 1:2]))
        return self.logistic(x)

    def siamese(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2(x), 2))
        x = F.relu(F.max_pool2d(self.conv3(x), 2))
        x = x.view(-1, 128 * 9 * 9)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

    def logistic(self, x):
        x = self.fc3(x)
        return torch.sigmoid(x)


#################################
#        Hyperparameters        #
#################################

N_characters = 20
im_height = 105
im_with = 105
val_split = 0.1
n_epochs = 252
# cut_off = 0.7

###################################
#            Data prep            #
###################################

images_train = read_data('omniglot/images_background', n_characters=20, im_height=105, im_with=105)
train_N_categories = images_train.shape[0]
np.random.shuffle(images_train)
images_val = images_train[int(train_N_categories * (1 - val_split)):]
images_train = images_train[:int(train_N_categories * (1 - val_split))]

images_test = read_data('omniglot/images_evaluation', n_characters=20, im_height=105, im_with=105)
test_N_categories = images_test.shape[0]

X_val, Y_val = transform_data(images_val, 1024, N_characters, im_height, im_with)
X_test, Y_test = transform_data(images_test, 1024, N_characters, im_height, im_with)

###################################
#            Model def            #
###################################

model = Net()
model.to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-4)

##################################
#            Training            #
##################################

train_loss = []
val_loss = []

tic = time.time()
for epoch in range(1, n_epochs + 1):
    X_train, Y_train = transform_data(images_train, 1024, N_characters, im_height, im_with)
    train_dataset = TensorDataset(X_train, Y_train)
    train_loader = DataLoader(train_dataset, batch_size=64)

    model.train()
    epoch_loss = []
    for data, target in train_loader:
        output = model(data)
        optimizer.zero_grad()
        loss = nn.BCELoss()(output, target)
        loss.backward()
        optimizer.step()
        epoch_loss.append(loss.item())
    train_loss.append(np.mean(epoch_loss))
    val_loss.append(nn.BCELoss()(model(X_val), Y_val).item())

    print(f'''Epoch {epoch}/{n_epochs} - {round(time.time() - tic, 1)}s -\
 Train loss: {train_loss[-1]:.8f} - Val loss: {val_loss[-1]:.8f}''')
    tic = time.time()

fig = plt.figure(figsize=(16, 12))
plt.plot(train_loss)
plt.plot(val_loss)
plt.legend(['Train loss', 'Validation loss'])
plt.title('Loss over epochs')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.savefig('loss.png')

#################################
#            Testing            #
#################################

Y_pred = torch.gt(model(X_test), 0.5).double()
confusion_matrix_test = np.zeros((2, 2), np.int32)
for i in range(2):
    for k in range(2):*
        confusion_matrix_test[i, k] = int(
            torch.sum(torch.eq(torch.eq(Y_pred, 1 - i).double() + torch.eq(Y_test, 1 - k).double(), 2)))
confusion_matrix_test = pd.DataFrame(confusion_matrix_test, index=['Predicted True', 'Predicted False'],
                                     columns=['Real True', 'Real False'])
print(confusion_matrix_test)

for cut_off in range(11):
    cut_off = 0.5 + cut_off / 20
    confusion_matrix = np.zeros((2, 2), np.int32)
    N_registered = int(0.1 * test_N_categories)
    idx_registered = np.random.choice(np.arange(test_N_categories), size=N_registered, replace=False)
    latent_registered = model.siamese(torch.from_numpy(images_test[idx_registered, 0:1]).float().to(device))
    result = np.zeros((test_N_categories, N_characters - 1))
    for i_cat in range(test_N_categories):
        latent_cat = model.siamese(torch.from_numpy(images_test[i_cat, 1:][:, np.newaxis]).float().to(device))
        for i_char in range(N_characters - 1):
            pred = model.logistic(torch.abs(latent_registered - latent_cat[i_char]))
            pred = torch.gt(pred, cut_off).double()
            # pred = torch.Tensor.cpu(pred).detach().numpy()
            result[i_cat, i_char] = 1 if torch.sum(pred) == 0 else 0

            if i_cat in idx_registered:
                if torch.sum(pred) == 0:
                    confusion_matrix[1, 0] += 1
                else:
                    confusion_matrix[0, 0] += 1
            else:
                if torch.sum(pred) == 0:
                    confusion_matrix[1, 1] += 1
                else:
                    confusion_matrix[0, 1] += 1

        if i_cat in idx_registered:
            result[i_cat] = 1 - result[i_cat]

    confusion_matrix = pd.DataFrame(confusion_matrix, index=['Predicted True', 'Predicted False'],
                                    columns=['Real True', 'Real False'])
    confusion_matrix.to_csv(f'confusion_matrix_{cut_off}.csv')
    print(cut_off)
    print(confusion_matrix)


