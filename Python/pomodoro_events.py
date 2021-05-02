import discord
import datetime
import csv
from events import *


class CheckStudyingCommand(Event):
    #  This is an event created when someone asks to see if another user is studying
    requested_user: discord.User

    def __init__(self, start_time, length, user_id, requested_user):
        super().__init__(start_time, length, user_id)
        self.requested_user = requested_user

    def run_event(self, event_queue: EventQueue):
        items = []
        with open('database/studying.csv', 'r') as users:
            for user in users:
                items.append(user)

        items = [item.strip('\n') for item in items]

        print(items)

        studying = False
        if str(self.requested_user) in items:
            studying = True

        if studying:
            event_queue.add(MessageEvent(self.start_time, self.length, "Yes, that user is currently study! You probably shouldn't bother them!", self.user_id))
        else:
            event_queue.add(MessageEvent(self.start_time, self.length, "No, that user isn't studying! Feel free to give them a call!", self.user_id))



class PomodoroCommand(Event):
    # This is created when a user runs the "+Pomodoro" command
    def run_event(self, event_queue):
        start_time = datetime.datetime.now() + datetime.timedelta(minutes=25)
        reminder_event = PomodoroBreakReminder(start_time, datetime.timedelta(), self.user_id)
        repeated_event = PomodoroRepeated(start_time, self.length, 4, reminder_event, self.user_id,
                                          datetime.timedelta(minutes=25))

        start_time_long = datetime.datetime.now() + datetime.timedelta(hours=2)
        reminder = PomodoroLongBreakReminder(start_time, datetime.timedelta(), self.user_id)
        repeated_long_event = RepeatedEvent(start_time_long, self.length, 1, reminder, True,
                                            self.user_id, datetime.timedelta(hours=2))

        event_queue.add_list([MessageEvent(datetime.datetime.now(), datetime.timedelta(),
                                           "Started the Pomodoro Studying method", self.user_id),
                              repeated_event, repeated_long_event])

        # Add the users name to the list of studying people
        items = []
        with open('database/studying.csv', 'r') as studying_users:
            reader = csv.reader(studying_users)
            for user in reader:
                items.append(user[0])

        if str(self.user_id) not in items:
            items.append(str(self.user_id))

            with open('database/studying.csv', 'w', newline='') as studying_users:
                writer = csv.writer(studying_users)
                for user in items:
                    writer.writerow([user])


class PomodoroLongBreakReminder(Event):
    reminder_text: str = 'Its time to take a break (30 minutes)'

    def run_event(self, event_queue: EventQueue):
        event_queue.add(
            MessageEvent(datetime.datetime.now(), datetime.timedelta(), self.reminder_text,
                         self.user_id))

    def clone_event(self):
        return PomodoroLongBreakReminder(self.start_time, self.length, self.user_id)


class PomodoroBreakReminder(Event):
    reminder_text: str = 'Its time to take a break (5 minutes)'

    def run_event(self, event_queue: EventQueue):
        event_queue.add(
            MessageEvent(datetime.datetime.now(), datetime.timedelta(), self.reminder_text,
                         self.user_id))

    def clone_event(self):
        return PomodoroBreakReminder(self.start_time, self.length, self.user_id)


class PomodoroRepeated(Event):
    num_of_repeats: int

    unending: bool

    time_interval: int  # The amount of time between the repetition of the event

    event: Event  # Event to be repeated

    def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, repeats: int,
                 event: Event, user_id, time_interval):
        super().__init__(start_time, length, user_id)
        self.num_of_repeats = repeats
        self.event = event
        # self.unending = unending
        self.time_interval = time_interval

    def create_next_repeated_event(self) -> Event:
        new_event = self.event.clone_event()
        new_event.start_time = new_event.start_time + self.time_interval

        if self.num_of_repeats == 0:
            return NullEvent(datetime.datetime.now(), datetime.timedelta(), self.user_id)

        clone = self.clone_event()
        clone.start_time = clone.start_time + self.time_interval + datetime.timedelta(minutes=5)
        clone.num_of_repeats -= 1
        return clone

    def run_event(self, event_queue: EventQueue):
        # Add the wrapped event to the queue to be executed right away
        # Create the next instance of RepeatedEvent and that to the queue

        event_queue.add_list([self.event,
                              MessageEvent(self.start_time + datetime.timedelta(minutes=5),
                                           self.length, "The Break is over", self.user_id),
                              self.create_next_repeated_event()])

    def clone_event(self):
        return PomodoroRepeated(self.start_time, self.length, self.num_of_repeats, self.event,
                                self.user_id, self.time_interval)
