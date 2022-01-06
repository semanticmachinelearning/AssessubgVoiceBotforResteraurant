import datetime


class Store:
    def __init__(self):
        super().__init__()
        self.day_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        self.times = [["12:00", "02:00"],
                      ["11:00", "01:00"],
                      ["12:00", "02:00"],
                      ["11:00", "01:00"],
                      ["12:00", "02:00"],
                      ["11:00", "01:00"],
                      ["11:00", "01:00"]]

    def get_open_close_time(self, intention):
        day_number = datetime.datetime.today().weekday()
        intention_split = intention.split(" ")
        day_word = intention_split[0]
        open_close = intention_split[1]
        if day_word == "tomorrow":
            day_number += 1
            if day_number > 6:
                day_number = 0
        elif day_word == "yesterday":
            day_number -= 1
            if day_number < 0:
                day_number = 6
        elif day_word != "today":
            day_number = self.day_of_week.index(day_word)
            day_word = "on " + day_word

        # day_word = self.day_of_week[day_number]
        index = 0
        if open_close == "close":
            index = 1
        return [open_close, self.times[day_number][index], day_word]
