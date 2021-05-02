import datetime
import discord
import csv
import random
from events import *

class MusicReqCommand(Event):

    def run_event(self, event_queue: EventQueue):
        music = []
        with open('database/music.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                music.append(row[0])

        message = "Here is some music to help you study! If you don't like this, try again to get a different one!" + '\n'
        message += random.choice(music)
        event_queue.add(MessageEvent(self.start_time, self.length, message, self.user_id))


class MeditationReqCommand(Event):

    def run_event(self, event_queue: EventQueue):
