import dataloader
from ann import ANN
from dataset import DataSet
from action import Action
from memory import Memory
from response import Response
from speech import Speech

# Flow control
conversing = True
test_mode = False

# Scripts, data sets etc
dictionary = dataloader.get_dictionary()
intentions = dataloader.get_intention_outputs()
actions = dataloader.get_actions()
responses = dataloader.get_responses()
corrections = dataloader.get_corrections()

intention_inputs = len(dictionary) + 4
intention_outputs = len(intentions)
intention_hidden = int(round((2 / 3) * intention_outputs))

memory = Memory(intentions, actions)
action = Action(dictionary, intention_inputs, intention_outputs)
speech = Speech(test_mode, corrections)
response = Response(responses, intentions, actions)

intention_data = DataSet(
    dataloader.get_training_data("IntentionData", action.nlp.pre_process, action.nlp.process_intention_input))
intention_ann = ANN(intention_inputs, intention_hidden, intention_outputs, "Data/IntentionModel.pth", intention_data)

# while True:
#     input()
#     print(speech.recognise_speech())

speech.speak(response.get_random_response("greeting")[0])

while conversing:
    if test_mode:
        text = input("You: ").lower()
    else:
        text = speech.recognise_speech()

    if text == "quit":
        conversing = False
        break

    words = action.nlp.pre_process(text)

    # Menu term combination & menu term placeholder replacement
    order_items, words = action.order.find_best_combination(words)
    order_items = action.order.fill_default_parameters(order_items)

    # Neural network input
    intention_input = action.nlp.process_intention_input(words, False)

    # Neural network prediction
    intention_index = intention_ann.model.get_predicted(intention_ann.model(intention_input))
    memory.update_intention(intention_index)

    # Perform actions
    memory = action.process(memory, order_items, words, text)

    # Response generation
    memory, response_text = response.formulate_response(memory)

    # Speech synthesis
    speech.speak(response_text)

    # Update variables
    memory.update_last_intention(intention_index)

    if memory.last_response == "finish":
        conversing = False

    print("")

print(action.order.order)
