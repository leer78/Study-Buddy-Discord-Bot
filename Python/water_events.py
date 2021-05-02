import datetime
import discord
import csv
from events import *

class WaterCommand(Event):
    # This starts the water for the day, reminder after each hour
    def run_event(self, event_queue):
        start_time = datetime.datetime.now() + datetime.timedelta(minutes=60)
        reminder_event = WaterReminder(start_time, datetime.timedelta(), self.user_id)
        repeated_event = RepeatedEvent(start_time, self.length, 1, reminder_event, True,
                                       self.user_id, datetime.timedelta(minutes=60))

        event_queue.add_list([MessageEvent(datetime.datetime.now(), datetime.timedelta(),
                                           "You've setup a hydration reminder for today. You will be reminded every hour to drink water!",
                                           self.user_id), repeated_event])


class WaterReminder(Event):
    reminder_text: str = "It's been an hour since you're last water reminder, have you drank your water for the hour?"

    def run_event(self, event_queue: EventQueue):
        event_queue.add(
            MessageEvent(datetime.datetime.now(), datetime.timedelta(), self.reminder_text,
                         self.user_id))

    def clone_event(self):
        return WaterReminder(self.start_time, self.length, self.user_id)


class BottleCommand(Event):
    # This is created when a user runs the "+Bottle" command, it adds one bottle to your total

    def run_event(self, event_queue):
        items = []
        num_of_bottles = 0
        with open('database/bottles.csv', 'r') as bottle_csv:
            reader = csv.reader(bottle_csv)

            for row in reader:
                items.append(row)
                if row[0] == str(self.user_id):
                    num_of_bottles = int(row[1])

        if num_of_bottles == 0:
            items.append([str(self.user_id), '1'])
        else:
            for item in items:
                if item[0] == str(self.user_id):
                    item[1] = str(int(item[1]) + 1)

        with open('database/bottles.csv', 'w', newline='') as bottle_csv:
            writer = csv.writer(bottle_csv)

            for item in items:
                writer.writerow(item)

        message = "One bottle has just been added to your daily total! You have now drank " + str(
            num_of_bottles + 1) + " bottle(s) today!"
        event_queue.add(
            MessageEvent(datetime.datetime.now(), datetime.timedelta(), message, self.user_id))
