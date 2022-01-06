import random


class Response:
    def __init__(self, responses, intentions, tasks):
        super().__init__()
        self.responses = responses
        self.intentions = intentions
        self.tasks = tasks
        self.requirement_0 = list(["missing", "invalid"])
        self.requirement_1 = list(["item", "variant", "size"])

        self.input_length = len(intentions) * 2 + len(self.tasks) * 2 + len(responses) + len(self.requirement_0) + len(
            self.requirement_1)

    def formulate_response(self, memory):
        response = []
        if len(memory.tasks) > 0:
            print("tasks:", memory.tasks)
            task = memory.tasks[0]
            item = task[2]
            info = task[3]
            # ask for more info so action can be completed
            if len(task[1]) > 0:
                requirement = task[1][0]
                if memory.intention == "provide options":
                    response = self.get_random_response("provide options")
                else:
                    response = self.get_random_response(requirement[0] + " " + requirement[1])
                    response[1] = response[1].split(" ")[0]
                response = self.swap_place_holder(response, "[0]", self.formulate_options(requirement[2], "or"))

            # if there are no requirements we can complete the task
            else:
                if task[0] == "order contents":
                    response = self.formulate_order_contents(info[0])
                else:
                    response = self.get_random_response(task[0])

                for i in range(len(info)):
                    response = self.swap_place_holder(response, "[" + str(i) + "]", info[i])
                del memory.tasks[0]

            response = self.swap_place_holder(response, "[item]", item[0])
            response = self.swap_place_holder(response, "[variant]", item[1])
            response = self.swap_place_holder(response, "[size]", item[2])

        # if there are no tasks, fall back to general flow of conversion
        else:
            if memory.intention == "greeting":
                response = self.get_random_response("greeting")
            elif memory.intention == "order start":
                response = self.get_random_response("order start")
            # elif memory.last_intention_index <= 23:
            elif not memory.get_memory("order complete"):
                if memory.last_response == "order next" and memory.intention in ["neutral", "no", "none"]:
                    memory.add_memory("order complete", True)
                    response = self.get_random_response("ask delivery or collection")
                elif memory.intention == "none":
                    response = self.get_random_response("none")
                else:
                    response = self.get_random_response("order next")
            else:
                if not memory.contains_memory("delivery or collection"):
                    response = self.get_random_response("ask delivery or collection")
                else:
                    if memory.get_memory("delivery or collection") == "delivery":
                        if not memory.contains_memory("address"):
                            response = self.ask_response(memory, "address")
                        elif not memory.contains_memory("number"):
                            response = self.ask_response(memory, "number")
                    elif memory.get_memory("delivery or collection") == "collection":
                        if not memory.contains_memory("name"):
                            response = self.ask_response(memory, "name")
                        elif not memory.contains_memory("number"):
                            response = self.ask_response(memory, "number")

        memory.last_response = response[1]
        return memory, response[0]

    def ask_response(self, memory, question):
        if memory.last_response == "ask " + question:
            return self.get_random_response("no " + question)
        elif memory.last_response == "no " + question or memory.last_response == "no " + question + " help":
            return self.get_random_response("no " + question + " help")
        return self.get_random_response("ask " + question)

    def swap_place_holder(self, response, place_holder, swap_object):
        sentence = response[0]
        if place_holder in sentence:
            if type(swap_object) == list:
                swap_object = self.formulate_options(swap_object[1], swap_object[0])
            sentence = sentence.replace(place_holder, str(swap_object))
        response[0] = sentence
        return response

    def get_random_response(self, response):
        responses = self.responses[response]
        max = len(responses) - 1
        index = random.randint(0, max)
        return [responses[index], response]

    @staticmethod
    def formulate_options(options, and_or):
        response = ""
        if len(options) == 1:
            return options[0]
        commas = len(options) - 2
        if commas > 0:
            for i in range(commas):
                response += options[i] + ", "
        response += options[commas] + " " + and_or + " " + options[commas + 1]
        return response

    def formulate_order_contents(self, info):
        if len(info[1]) > 0:
            response = "You've got "
            items = list()
            for x in info[1]:
                item = "a " + x[2] + " " + x[1] + " " + x[0]
                for i in x[3]:
                    if i[0] == "extra":
                        item += " with extra " + i[1]
                    elif i[0] == "remove":
                        item += " without " + i[1]
                items.append(item)
            response += self.formulate_options(items, info[0])
        else:
            response = "You don't have anything on your order yet"
        return [response, "order contents"]
