import nltk
import numpy as np
import spacy
import torch
from word2number import w2n

nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
import pyap


class NLP:
    def __init__(self, dictionary, input_length):
        super().__init__()
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.dictionary = self.pre_process_dictionary(dictionary)
        self.input_length = input_length
        self.nlp = spacy.load("en_core_web_sm")

    def pre_process(self, message) -> []:
        message = message.lower()
        for character in message:
            if character not in ["[", "]", " ", "'", "-"]:
                asc_val = ord(character)
                if not ((48 <= asc_val <= 57) or (97 <= asc_val <= 122)):
                    message = message.replace(character, "")

        if " " in message:
            words = message.split(" ")
        else:
            words = [message]

        for i in range(len(words)):
            words[i] = self.lemmatizer.lemmatize(words[i])
            # words[i] = self.stemmer.stem(words[i])
        return words

    def process_intention_input(self, words, init) -> []:
        output = [np.float32(0)] * self.input_length
        one = np.float32(1)

        menu_terms = ["[item]", "[variant]", "[size]", "[customisable]"]
        for i in range(len(menu_terms)):
            if menu_terms[i] in words:
                output[len(output) - i - 1] = one

        for word in words:
            try:
                if word != "":
                    index = self.dictionary.index(word)
                    output[index] = one
            except ValueError:
                pass

        if not init:
            output = np.array(output)
            output = output.reshape(1, output.shape[0])
            output = torch.from_numpy(output).to("cpu")

        return output

    def pre_process_dictionary(self, dictionary):
        for i in range(len(dictionary)):
            dictionary[i] = self.lemmatizer.lemmatize(dictionary[i])
        return dictionary

    def process_nlp(self, message, looking_for, memory):

        tags = self.nlp(message)

        if "name" in looking_for:
            name = ""
            for word in tags:
                if word.pos_ == "PROPN":
                    name += word.text + " "
            if name != "":
                memory.add_memory("name", name[:-1])

        if "address" in looking_for:
            address = pyap.parse(message, country="GB")
            if len(address) > 0:
                memory.add_memory("address", address[0])

        if "number" in looking_for:
            for word in tags:
                if word.pos_ == "NUM":
                    if len(word.text) == 11:
                        memory.add_memory("number", word.text)

        return memory

    def pos_get_quantities(self, message):
        quantities = []
        tags = self.nlp(message)
        for tag in tags:
            if tag.pos_ == "X" or tag.pos_ == "NUM":
                try:
                    number = int(tag.text)
                except ValueError:
                    number = w2n.word_to_num(tag.text)
                quantities.append(number)
            else:
                quantities.append(None)
        return quantities
