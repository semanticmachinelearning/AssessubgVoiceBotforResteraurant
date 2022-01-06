class Memory:
    def __init__(self, intentions, actions):
        super().__init__()
        self.tasks = list()
        self.memory = list()
        self.add_memory("order complete", False)

        self.last_response_index = 0
        self.last_response = "none"

        self.last_action_index = 0
        self.last_action = "none"

        self.intention_index = 0
        self.intention = "none"

        self.last_intention_index = 27
        self.last_intention = "none"

        self.intentions = intentions
        self.actions = actions

    def add_task(self, task, requirements, item, variant, size, modifications, info):
        self.tasks.append([task, requirements, [item, variant, size, modifications], info])

    def update_last_action(self, intention):
        if intention in self.actions:
            self.last_action = intention
            self.last_action_index = self.actions.index(intention)

    def update_intention(self, index):
        self.intention_index = index
        self.intention = self.intentions[index]
        self.update_last_action(self.intention)

    def update_last_intention(self, index):
        self.last_intention_index = index
        self.last_intention = self.intentions[index]

    def add_memory(self, memory_type, value):
        contains_type = False
        for i in range(len(self.memory)):
            if self.memory[i][0] == memory_type:
                contains_type = True
                self.memory[i][1] = value
                break
        if not contains_type:
            self.memory.append([memory_type, value])

    def get_memory(self, memory_type):
        for memory in self.memory:
            if memory[0] == memory_type:
                return memory[1]
        return ""

    def contains_memory(self, memory_type):
        memory = self.get_memory(memory_type)
        return not (memory == "")
