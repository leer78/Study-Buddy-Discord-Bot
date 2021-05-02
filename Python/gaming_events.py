import discord
import datetime
import csv
from events import *


class GamingReminderEvent(Event):

    message = "Hey! You've been gaming for an hour now, you should take a 5 minute break to move around!"

    def run_event(self, event_queue):
        event_queue.add(MessageEvent(self.start_time, self.length, self.message, self.user_id))

    def clone_event(self):
        return GamingReminderEvent(self.start_time, self.length, self.user_id)


class GamingCommand(Event):

    def run_event(self, event_queue: EventQueue):
        turning_on = True

        with open('database/gaming_users.csv', 'r') as users:
            reader = csv.reader(users)

            for row in reader:
                if row[0] == str(self.user_id):
                    turning_on = False
            users.close()

        if turning_on:
            output = "You have started a gaming session! You will now be reminded every hour to take a break and get some exercise. To end your session, run +gaming again."
            event_queue.add(MessageEvent(datetime.datetime.now(), datetime.timedelta(), output, self.user_id))

            with open('database/gaming_users.csv', 'a', newline='') as users:
                writer = csv.writer(users)
                writer.writerow([str(self.user_id)])

            new_start_time = self.start_time + datetime.timedelta(minutes=1)
            repeated_message_event = GamingReminderEvent(new_start_time, datetime.timedelta(), self.user_id)
            repeated_event = RepeatedEvent(new_start_time, datetime.timedelta(), 1, repeated_message_event, True, self.user_id, datetime.timedelta(minutes=1))
            event_queue.add(repeated_event)

        else:
            output = "You have just ended your gaming session! To start another one, run +gaming again."
            event_queue.add(MessageEvent(datetime.datetime.now(), datetime.timedelta(), output, self.user_id))

            items = []
            with open('database/gaming_users.csv', 'r', newline='') as users:
                reader = csv.reader(users)
                for row in reader:
                    items.append(row[0])

            items.remove(str(self.user_id))

            with open('database/gaming_users.csv', 'w', newline='') as users:
                writer = csv.writer(users)
                for item in items:
                    writer.writerow([item])

            for i in range(0, len(event_queue.events)):
                if isinstance(event_queue.events[i], RepeatedEvent):
                    if isinstance(event_queue.events[i].event, GamingReminderEvent):
                        event_queue.events[i] = NullEvent(self.start_time, self.length, self.user_id)
