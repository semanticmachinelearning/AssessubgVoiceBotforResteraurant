import random

import torch
import torch.nn as nn

flatten = lambda l: [item for sublist in l for item in sublist]
random.seed(1024)


# class Net(nn.Module):
#     def __init__(self, vocab_size, embedding_size, hidden_size, n_layers=1, dropout_p=0.5):
#         super(Net, self).__init__()
#         self.n_layers = n_layers
#         self.hidden_size = hidden_size
#         self.embed = nn.Embedding(vocab_size, embedding_size)
#         self.rnn = nn.LSTM(embedding_size, hidden_size, n_layers, batch_first=True)
#         self.linear = nn.Linear(hidden_size, vocab_size)
#         self.dropout = nn.Dropout(dropout_p)
#         self.USE_CUDA = False
#
#     def init_weight(self):
#         self.embed.weight = nn.init.xavier_uniform_(self.embed.weight)
#         self.linear.weight = nn.init.xavier_uniform_(self.linear.weight)
#         self.linear.bias.data.fill_(0)
#
#     def init_hidden(self, batch_size):
#         hidden = Variable(torch.zeros(self.n_layers, batch_size, self.hidden_size))
#         context = Variable(torch.zeros(self.n_layers, batch_size, self.hidden_size))
#         return (hidden.cuda(), context.cuda()) if self.USE_CUDA else (hidden, context)
#
#     def detach_hidden(self, hiddens):
#         return tuple([hidden.detach() for hidden in hiddens])
#
#     def forward(self, inputs, hidden, is_training=False):
#         embeds = self.embed(inputs)
#         if is_training:
#             embeds = self.dropout(embeds)
#         out, hidden = self.rnn(embeds, hidden)
#         return self.linear(out.contiguous().view(out.size(0) * out.size(1), -1)), hidden

class Net(nn.Module):
    def __init__(self, inputs, hidden_layers, outputs):
        super(Net, self).__init__()

        self.l1 = nn.Linear(inputs, hidden_layers)
        # self.l2 = nn.Linear(hidden_layers, hidden_layers)
        self.l3 = nn.Linear(hidden_layers, outputs)
        self.relu = nn.ReLU()

        # self.layers = []
        # self.layers.append(nn.Linear(inputs, hidden_layers[0]))
        # for i in range(len(hidden_layers) - 1):
        #     self.layers.append(nn.Linear(hidden_layers[i], hidden_layers[i + 1]))
        # self.layers.append(nn.Linear(hidden_layers[i], outputs))

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        # out = self.l2(out)
        # out = self.relu(out)
        out = self.l3(out)
        return out

    def get_predicted(self, output):
        _, predicted = torch.max(output, dim=1)
        predicted = predicted.item()
        return predicted
