class DataSet:
    def __init__(self, data):
        self.x = data[0]
        self.y = data[1]
        self.length = len(self.x)

    def __getitem__(self, index):
        return self.x[index], self.y[index]

    def __len__(self):
        return self.length
