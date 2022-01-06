from memory import Memory
from nlp import NLP
from order import Order
from store import Store


class Action:
    def __init__(self, dictionary, intention_inputs, intention_outputs):
        super().__init__()
        self.nlp = NLP(dictionary, intention_inputs)
        self.order = Order(intention_outputs)
        self.store = Store()

    def process(self, memory: Memory, order_items, words, text):

        if memory.intention == "previous query" and memory.last_action != "none":
            current_intention = memory.last_action

        # order_input = format_ann_input(order.process_input(new_message))
        # order_output = order_ann.model.get_predicted(order_ann.model(order_input)
        # quantities = nlp.pos_get_quantities(texts[i])
        quantities = []
        item_info = self.order.order_items_sentence_to_array(order_items)

        print("intention:", memory.intention)
        if memory.intention_index <= 23:
            memory = self.order.process_output(memory.intention, memory.intention_index, order_items, quantities,
                                               memory)
            print("order:", self.order.order)
        else:
            if memory.intention == "provide options" and memory.last_response not in ["missing", "invalid", "need"]:
                memory.add_task("provide options", [], "", "", "", [], [["or", self.order.get_items()]])
            elif memory.intention == "order price":
                memory.add_task("order price", [], "", "", "", [], [self.order.get_order_price()])
            elif memory.intention == "item price":
                memory = self.order.process_item_price(item_info, memory)
            elif memory.intention == "provide variants":
                memory = self.order.process_provide_variant_or_size(item_info, "provide variants", memory)
            elif memory.intention == "provide sizes":
                memory = self.order.process_provide_variant_or_size(item_info, "provide sizes", memory)
            elif 35 <= memory.intention_index <= 54:
                memory.add_task("open close time", [], "", "", "", [], self.store.get_open_close_time(memory.intention))
            elif memory.intention == "order contents":
                memory.add_task("order contents", [], "", "", "", [], [["and", self.order.order]])
            elif memory.last_response == "ask delivery or collection":
                # There is sometimes a bug where the NN doesn't recognise intentions for delivery and collection
                if "delivery" in words:
                    memory.intention = "delivery"
                elif "collection" in words:
                    memory.intention = "collection"
                memory.add_memory("delivery or collection", memory.intention)
            else:
                try:
                    if memory.last_response.split(" ")[1] in ["name", "address", "number"]:
                        memory = self.nlp.process_nlp(text, [memory.last_response.split(" ")[1]], memory)
                except IndexError:
                    pass

        # get price if all parameters are filled
        for task in memory.tasks:
            if task[0] == "item price" and task[2][0] != "" and task[2][1] != "" and task[2][2] != "" and task[3][
                0] == 0.0:
                task[3][0] = self.order.get_item_price(task[2][0], task[2][1], task[2][2], task[2][3])

        return memory
