import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from model import Net


class ANN:
    def __init__(self, input_size, hidden_size, output_size, model_path, training_data):
        self.path = model_path
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.num_epochs = 1000

        # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = torch.device("cpu")
        self.model = Net(input_size, hidden_size, output_size).to(self.device)

        self.criterion = nn.CrossEntropyLoss()
        self.optimiser = torch.optim.Adam(self.model.parameters(), lr=0.001)

        self.training_data = DataLoader(dataset=training_data, batch_size=1, shuffle=True)
        self.load()

    def train(self):
        for epoch in range(self.num_epochs):
            for (words, labels) in self.training_data:
                words = words.to(self.device)
                labels = labels.to(dtype=torch.long).to(self.device)

                outputs = self.model(words)
                loss = self.criterion(outputs, labels)

                self.optimiser.zero_grad()
                loss.backward()
                self.optimiser.step()

            if (epoch + 1) % 100 == 0:
                print(f'Epoch [{epoch + 1}/{self.num_epochs}], Loss: {loss.item():.4f}')

        print(f'final loss: {loss.item():.4f}')

        torch.save(self.model.state_dict(), self.path)

    def load(self):
        try:
            state_dictionary = torch.load(self.path, map_location=self.device)
            self.model.load_state_dict(state_dictionary)
            self.model.eval()
        except IOError:
            self.train()
