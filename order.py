import dataloader


class Order:
    def __init__(self, intentions):
        super().__init__()
        self.menu = dataloader.get_menu()
        self.items, self.variants, self.sizes, self.customisables = self.get_menu_groups()
        self.menu_words = self.get_menu_words()
        self.outputs = intentions
        self.types = ["item", "variant", "size", "customisable"]

        self.order = []

    def get_items(self):
        return list(self.menu["item"].keys())

    def get_item_customisables(self, item, variant):
        return list(self.menu["item"][item]["variant"][variant]["customisable"])

    def get_item_variants(self, item):
        return list(self.menu["item"][item]["variant"].keys())

    def get_item_sizes(self, item):
        return list(self.menu["item"][item]["size"])

    def process_output(self, intention, intention_index, order_items, quantities, memory):
        add_item, remove_item, includes_item, includes_variant, includes_size, \
        add_customisable, remove_customisable, abs_customisable = self.intention_output_to_bools(intention)

        item_info = self.order_items_sentence_to_array(order_items)
        # item, variant, size, modifications = self.order_items_array_to_variables(item_info)

        if intention == "":
            pass

        if len(memory.tasks) > 0:
            task = memory.tasks[0]
            if task[0] in ["order add", "item price"]:
                item = task[2]
                # ask for more info so action can be completed
                for requirement in task[1]:
                    if requirement[0] in ["missing", "invalid", "need"]:
                        if requirement[1] == "variant":
                            variant = self.get_word_by_index("variant", order_items, 0)
                            if variant == "":
                                variant = self.get_word_by_index("customisable", order_items, 0)
                            if variant in requirement[2]:
                                item[1] = variant
                                task[1].remove(requirement)
                        elif requirement[1] == "size":
                            size = self.get_word_by_index("size", order_items, 0)
                            if size in requirement[2]:
                                item[2] = size
                                task[1].remove(requirement)
                task[2] = item

                if len(task[1]) == 0 and task[0] == "order add":
                    self.add_item(task[2][0], task[2][1], task[2][2], task[2][3])
                    memory.tasks.remove(task)

        new_tasks = []

        if not item_info:
            pass
        elif add_item:
            item, variant, size = "", "", ""
            possible_variants, possible_sizes, modifications = [], [], []
            invalid_variant, invalid_size = False, False

            if includes_item:
                item = self.get_word_by_index("item", order_items, 0)
                # Possibility of not including item
                if item != "":
                    if includes_variant:
                        variant = self.get_word_by_index("variant", order_items, 0)
                        if not self.verify_valid_type(item, ["variant", variant]):
                            new_tasks.append(["invalid", "variant", self.get_possible_types(["item", item], "variant")])
                            variant = ""
                            invalid_variant = True
                    if includes_size:
                        size = self.get_word_by_index("size", order_items, 0)
                        if not self.verify_valid_type(item, ["size", size]):
                            new_tasks.append(["invalid", "size", self.get_possible_types(["item", item], "size")])
                            size = ""
                            invalid_size = True
                else:
                    includes_item = False
            else:
                pass
                # Do something when there isn't an item

            if includes_item:
                if not includes_variant:
                    variant_result = self.get_default_or_possible_variants(item)
                    if type(variant_result) == str:
                        variant = variant_result
                    else:
                        possible_variants = variant_result

                if not includes_size:
                    size_result = self.get_default_or_possible_sizes(item)
                    if type(size_result) == str:
                        size = size_result
                    else:
                        possible_sizes = size_result

            else:
                pass
                # Find item if includes variant and size if possible

            # CUSTOMISABLE
            if add_customisable or remove_customisable or abs_customisable:
                customisable = self.get_word_by_index("customisable", order_items, 0)
                customisation = ""
                if add_customisable:
                    customisation = "extra"
                elif remove_customisable:
                    customisation = "remove"
                elif abs_customisable:
                    customisation = "absolute"
                modifications.append([customisation, customisable])

            if item != "" and variant != "" and size != "":
                self.add_item(item, variant, size, modifications)
            else:
                if len(possible_variants) > 0 and not invalid_variant:
                    new_tasks.append(["missing", "variant", self.get_possible_types(["item", item], "variant")])
                if len(possible_sizes) > 0 and not invalid_size:
                    new_tasks.append(["missing", "size", self.get_possible_types(["item", item], "size")])

            if len(new_tasks) > 0:
                memory.add_task("order add", new_tasks, item, variant, size, modifications, [])

        elif remove_item:
            item = self.get_word_by_index("item", order_items, 0)
            if item != "":
                for i in range(len(self.order)):
                    if self.order[i][0] == item:
                        self.remove_item(i)
                        break
            else:
                self.remove_item(-1)

        return memory

    def get_requirements(self, item, variant, size, type_, return_defaults=True):
        requirements = []
        if item == "":
            requirements.append([type_, "item", self.get_items()])
            variant, size = "", ""
        else:
            if variant == "":
                variant_result = self.get_default_or_possible_variants(item)
                if type(variant_result) == str:
                    variant = variant_result
                else:
                    requirements.append([type_, "variant", variant_result])
            else:
                if not self.verify_valid_type(item, ["variant", variant]):
                    requirements.append(["invalid", "variant", self.get_possible_types(["item", item], "variant")])

            if size == "":
                size_result = self.get_default_or_possible_sizes(item)
                if type(size_result) == str:
                    size = size_result
                else:
                    requirements.append([type_, "size", size_result])
            else:
                if not self.verify_valid_type(item, ["size", size]):
                    requirements.append(["invalid", "size", self.get_possible_types(["item", item], "size")])

        if return_defaults:
            return variant, size, requirements
        else:
            return requirements

    def fill_default_parameters(self, item_info):
        item, variant, size = "", "", ""
        for i in item_info:
            if i[0] == "item":
                item = i[1]
            elif i[0] == "variant":
                variant = i[1]
            elif i[0] == "size":
                size = i[1]
        if item != "":
            if variant == "":
                variant = self.get_default_or_possible_variants(item)
                if type(variant) == str:
                    item_info.append(["variant", variant])
            if size == "":
                size = self.get_default_or_possible_variants(item)
                if type(size) == str:
                    item_info.append(["variant", size])
        return item_info

    def get_default_or_possible_variants(self, item):
        default_variant = self.menu["item"][item]["default variant"]
        if default_variant == "none":
            return self.get_possible_types(["item", item], "variant")
        else:
            return default_variant

    def get_default_or_possible_sizes(self, item):
        default_size = self.menu["item"][item]["default size"]
        if default_size == "none":
            return self.get_possible_types(["item", item], "size")
        else:
            return default_size

    def get_word_by_index(self, type, array, index):
        types = self.word_types_by_type(type, array)
        if len(types) > 0:
            return types[index][1]
        return ""

    def intention_output_to_bools(self, intention):
        contains = intention.split(" ")
        add_item = "add" in contains
        remove_item = "remove" in contains
        includes_item = "item" in contains
        includes_variant = "variant" in contains
        includes_size = "size" in contains
        add_customisable = "+custom" in contains
        remove_customisable = "-custom" in contains
        abs_customisable = "abscustom" in contains
        return add_item, remove_item, includes_item, includes_variant, includes_size, add_customisable, remove_customisable, abs_customisable

    def find_best_combination(self, words):

        if len(words) > 0:
            combination_sets = self.split(words)
            word_sets = []
            validations = []
            if len(words) > 1:
                for combination_set in combination_sets:
                    word_set = []
                    for combination in combination_set:
                        sentence = self.form_sentence(combination)
                        word_set.append(sentence)
                    word_sets.append(word_set)
            else:
                word_sets.append(words)
            best_length_found = 0
            best_word_order = []
            for word_set in word_sets:
                length_found = 0
                word_order = []
                for word in word_set:
                    words_found = []
                    if word in self.items:
                        words_found.append(["item", word])
                        length_found += len(word.split(" "))
                    if word in self.variants:
                        words_found.append(["variant", word])
                        length_found += len(word.split(" "))
                    if word in self.sizes:
                        words_found.append(["size", word])
                        length_found += len(word.split(" "))
                    if word in self.customisables:
                        words_found.append(["customisable", word])
                        length_found += len(word.split(" "))
                    if len(words_found) > 0:
                        word_order.append(words_found)
                    else:
                        word_order.append([["filler", word]])
                if length_found > best_length_found:
                    best_length_found = length_found
                    best_word_order = word_order

            if best_length_found == 0:
                best_word_order = [[["filler", word_sets[0][0]]]]

            final_word_order = []
            indices_to_change = []
            for i in range(len(best_word_order)):
                if len(best_word_order[i]) == 1:
                    final_word_order.append(best_word_order[i][0])
                else:
                    final_word_order.append([])
                    indices_to_change.append(i)

            for index in indices_to_change:
                options = []
                for word_type in best_word_order[index]:
                    options.append(word_type[0])

                before_item = False
                after_filler = False
                between_fillers = False
                before_empty = False
                if index < len(final_word_order) - 1:
                    if len(final_word_order[index + 1]) > 0:
                        if final_word_order[index + 1][0] == "item":
                            before_item = True
                    else:
                        before_empty = True
                if index > 0:
                    if len(final_word_order[index - 1]) > 0:
                        if final_word_order[index - 1][0] == "filler":
                            after_filler = True
                            if index < len(final_word_order) - 1:
                                if len(final_word_order[index + 1]) > 0:
                                    if final_word_order[index + 1][0] == "filler":
                                        between_fillers = True

                type = ""
                if before_item != after_filler:
                    if before_item:
                        type = "variant"
                    if after_filler:
                        type = "customisable"
                elif between_fillers:
                    type = "extra"
                else:
                    type = "variant"

                final_word_order[index] = self.word_types_by_type(type, best_word_order[index])[0]

            new_words = []
            for word_type in final_word_order:
                if word_type[0] == "filler":
                    split = word_type[1].split(" ")
                    for i in split:
                        new_words.append(i)
                else:
                    new_words.append("[" + word_type[0] + "]")
            return final_word_order, new_words
        else:
            return [], words

    def split(self, words):
        if len(words) > 1:
            combination_count = pow(2, len(words) - 1)
            activation_sets = []
            for i in range(combination_count):
                activation = bin(i)[2:]
                while len(activation) < len(words) - 1:
                    activation = "0" + activation
                activation_bool = []
                for x in activation:
                    active = x != "0"
                    # active = True
                    # if x == "0":
                    #     active = False
                    activation_bool.append(active)
                activation_sets.append(activation_bool)

            combinations = []
            for activation_set in activation_sets:
                combination = []
                sentence = [words[0]]
                for i in range(len(activation_set)):
                    if activation_set[i]:
                        combination.append(sentence)
                        sentence = []
                    sentence.append(words[i + 1])
                combination.append(sentence)
                combinations.append(combination)
            return combinations
        else:
            return words

    def form_sentence(self, words):
        sentence = words[0]
        for i in range(len(words) - 1):
            sentence += " " + words[i + 1]
        return sentence

    def word_types_by_word(self, word, array):
        word_types = []
        for i in range(len(array)):
            if word == array[i][1]:
                word_types.append(array[i])
        return word_types

    def word_types_by_type(self, type, array):
        word_types = []
        for i in range(len(array)):
            if type == array[i][0]:
                word_types.append(array[i])
        return word_types

    def get_possible_types(self, word_type, associated_type):
        type_ = word_type[0]
        word = word_type[1]
        possible_types = []
        if type_ == "item" and associated_type != "item":
            possible_types = self.menu["item"][word][associated_type]
            if type(possible_types) != list:
                possible_types = list(possible_types.keys())
            return possible_types
        elif type_ == "variant" and associated_type == "item":
            for item in self.menu["item"].keys():
                variants = list(self.menu["item"][item]["variant"].keys())
                if word in variants:
                    possible_types.append(item)
        elif type_ == "size" and associated_type == "item":
            for item in self.menu["item"].keys():
                sizes = self.menu["item"][item]["size"]
                if word in sizes:
                    possible_types.append(item)
        return possible_types

    def add_item(self, item, variant, size, modifications):
        self.order.append([item, variant, size, modifications])

    def remove_item(self, index):
        del self.order[index]

    def get_order_price(self):
        cost = 0.0
        for item in self.order:
            cost += self.get_item_price(item[0], item[1], item[2], item[3])
        return cost

    def get_item_price(self, item, variant, size, modifications):
        return float(self.menu["item"][item]["variant"][variant]["size"][size])

    def process_item_price(self, item_info, memory):
        item, variant, size, modifications = self.order_items_array_to_variables(item_info)
        variant_result, size_result, requirements = self.get_requirements(item, variant, size, "need", True)
        valid_item, valid_variant, valid_size = True, True, True
        for requirement in requirements:
            if requirement[1] == "item":
                valid_item = False
            elif requirement[0] == "invalid":
                if requirement[1] == "variant":
                    valid_variant = False
                elif requirement[1] == "size":
                    valid_size = False

        if valid_item:
            if valid_variant:
                if variant == "" and variant_result != "":
                    variant = variant_result
            else:
                variant = ""
            if valid_size:
                if size == "" and size_result != "":
                    size = size_result
            else:
                size = ""

        price = 0.0
        if item != "" and variant != "" and size != "":
            price = self.get_item_price(item, variant, size, modifications)
        memory.add_task("item price", requirements, item, variant, size, modifications, [price])
        return memory

    def process_provide_variant_or_size(self, item_info, variant_or_size, memory):
        item, variant, size, modifications = self.order_items_array_to_variables(item_info)
        if item == "":
            memory.add_task(variant_or_size, [["need", "item", self.get_items()]], item, variant, size, modifications,
                            [])
        else:
            if variant_or_size == "provide variants":
                memory.add_task(variant_or_size, [], item, variant, size, modifications,
                                [["and", self.get_item_variants(item)]])
            else:
                memory.add_task(variant_or_size, [], item, variant, size, modifications,
                                [["and", self.get_item_sizes(item)]])
        return memory

    def order_items_sentence_to_array(self, order_items):
        result = ["", "", "", []]
        for word in order_items:
            if word[0] == "item":
                result[0] = word[1]
            elif word[0] == "variant":
                result[1] = word[1]
            elif word[0] == "size":
                result[2] = word[1]
        return result

    def order_items_array_to_variables(self, order_items):
        return order_items[0], order_items[1], order_items[2], order_items[3]

    def verify_valid_type(self, item, word_type):
        try:
            values = self.menu["item"][item][word_type[0]].keys()
        except AttributeError:
            values = self.menu["item"][item][word_type[0]]
        for value in values:
            if value == word_type[1]:
                return True
        return False

    def get_menu_words(self):
        words = list()
        items = list(self.menu["item"].keys())
        for item in items:
            item_split = item.split(" ")
            for item_word in item_split:
                if item_word not in words:
                    words.append(item_word)
            variants = list(self.menu["item"][item]["variant"])
            for variant in variants:
                variant_split = variant.split(" ")
                for variant_word in variant_split:
                    if variant_word != "default" and variant_word not in words:
                        words.append(variant_word)
                sizes = list(self.menu["item"][item]["variant"][variant]["size"])
                for size in sizes:
                    size_split = size.split(" ")
                    for size_word in size_split:
                        if size_word != "standard" and size_word not in words:
                            words.append(size_word)
                customisables = list(self.menu["item"][item]["variant"][variant]["customisable"])
                for customisable in customisables:
                    customisable_split = customisable.split(" ")
                    for customisable_word in customisable_split:
                        if customisable_word not in words:
                            words.append(customisable_word)
            extras = list(self.menu["item"][item]["extra"])
            for extra in extras:
                if extra not in words:
                    words.append(extra)
        return words

    def get_menu_groups(self):
        items = list(self.menu["item"].keys())
        variants = list()
        sizes = list()
        customisables = list()
        for item in items:
            variant_keys = list(self.menu["item"][item]["variant"].keys())
            for variant in variant_keys:
                if variant not in variants:
                    variants.append(variant)
                size_keys = list(self.menu["item"][item]["variant"][variant]["size"].keys())
                for size in size_keys:
                    if size not in sizes:
                        sizes.append(size)
                customisable_keys = self.menu["item"][item]["variant"][variant]["customisable"]
                for customisable in customisable_keys:
                    if customisable not in customisables:
                        customisables.append(customisable)
            extra_values = list(self.menu["item"][item]["extra"])
            for extra in extra_values:
                if extra not in customisables:
                    customisables.append(extra)
        return items, variants, sizes, customisables
    #
    # @staticmethod
    # def contains_word(w):
    #     return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
