pip3 install numpy
import csv
import io
import json

import numpy as np


def get_training_data(data_set, pre_process_function, process_function):
    x = []
    y = []
    with io.open("Data/" + data_set + ".csv", "r") as data_file:
        content = csv.reader(data_file)
        for sentence in content:
            training_input = pre_process_function(sentence[0])
            training_input = process_function(training_input, True)
            for i in range(len(training_input)):
                training_input[i] = np.float32(training_input[i])
            x.append(training_input)
            y.append(int(sentence[1]))
        x = np.array(x)
        y = np.array(y)
    return [x, y]


def get_dictionary() -> []:
    with io.open("Data/Dictionary.csv", "r") as dictionary_file:
        content = dictionary_file.read().split("\n")
    return content


def get_menu() -> {}:
    with io.open("Data/Menu.json", "r") as menu_file:
        content = menu_file.read()
        menu_dictionary = json.loads(content)
    return menu_dictionary


def get_responses() -> {}:
    with io.open("Data/Responses.json", "r") as responses_file:
        content = responses_file.read()
        responses = json.loads(content)
    return responses


def get_actions() -> []:
    outputs = []
    with io.open("Data/Actions.csv", "r") as actions_file:
        content = csv.reader(actions_file)
        for line in content:
            outputs.append(line[0])
    return outputs


def get_intention_outputs() -> []:
    outputs = []
    with io.open("Data/IntentionOutputs.csv", "r") as outputs_file:
        content = csv.reader(outputs_file)
        for line in content:
            outputs.append(line[0])
    return outputs


def get_corrections() -> {}:
    with io.open("Data/SpeechRecognitionCorrections.json", "r") as corrections_file:
        content = corrections_file.read()
        corrections = json.loads(content)
    return corrections
