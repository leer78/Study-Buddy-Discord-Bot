import datetime
import time
import discord
import csv


class Event:
	user_id: discord.User

	start_time: datetime.datetime
	length: datetime.timedelta
	end_time: datetime.datetime

	def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, user_id: discord.User):
		self.user_id = user_id

		self.start_time = start_time
		self.length = length

		self.end_time = self.start_time + self.length

	def run_event(self, event_queue):
		raise NotImplementedError

	def clone_event(self):
		raise NotImplementedError


class EventQueue:
	# The events sorted decreasing order of the timedelta from the current time
	events: list[Event]

	def __init__(self):
		self.events = []

	def add(self, event: Event):
		self.events.append(event)

		self.events.sort(key= lambda e: e.start_time - datetime.datetime.now(), reverse=True)
	
	def add_list(self, new_events: list[Event]):
		for e in new_events:
			self.events.append(e)
		
		self.events.sort(key=lambda ev: ev.start_time - datetime.datetime.now(), reverse=True)

	def pop(self):
		return self.events.pop()

	def is_empty(self) -> bool:
		if len(self.events) == 0:
			return True
		return False

	def is_ready(self) -> bool:
		if len(self.events) == 0:
			return False		

		if self.events[len(self.events) - 1].start_time - datetime.datetime.now() <= datetime.timedelta():
			return True
		
		return False

	def remove(self, event):
		for e in self.events:
			if e == event:
				self.events.remove(e)

	def view(self):
		for x in self.events:
			print(x.start_time)


class RepeatedEvent(Event):
	num_of_repeats: int

	unending: bool

	time_interval: int # The amount of time between the repetition of the event

	event: Event # Event to be repeated

	def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, repeats: int, event: Event, unending: bool, user_id, time_interval):
		super().__init__(start_time, length, user_id)
		self.num_of_repeats = repeats
		self.event = event
		self.unending = unending
		self.time_interval = time_interval

	def create_next_repeated_event(self) -> Event:
		new_event = self.event.clone_event()
		new_event.start_time = new_event.start_time + self.time_interval

		if self.unending:
			clone = self.clone_event()
			clone.start_time = clone.start_time + self.time_interval
			return clone
		
		if self.num_of_repeats == 0:
			return NullEvent(datetime.datetime.now(), datetime.timedelta(), self.user_id)

		clone = self.clone_event()
		clone.start_time = clone.start_time + self.time_interval
		clone.num_of_repeats -= 1
		return clone

	def run_event(self, event_queue: EventQueue):
		# Add the wrapped event to the queue to be executed right away
		# Create the next instance of RepeatedEvent and that to the queue

		event_queue.add_list([self.event, self.create_next_repeated_event()])
	
	def clone_event(self):
		return RepeatedEvent(self.start_time, self.length, self.num_of_repeats, self.event, self.unending, self.user_id, self.time_interval)


class NullEvent(Event):

	def run_event(self, event_queue):
		return None


class MessageEvent(Event):

	message_content: str

	def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, message: str, user_id):
		super().__init__(start_time, length, user_id)
		self.message_content = message

	def run_event(self, event_queue):
		return self.message_content
	
	def clone_event(self):
		return MessageEvent(self.start_time, self.length, self.message_content, self.user_id)


class EyeStrainReminder(Event):
	reminder_text: str = 'You need to look away now'

	def run_event(self, event_queue: EventQueue):
		event_queue.add(MessageEvent(datetime.datetime.now(), datetime.timedelta(), self.reminder_text, self.user_id))
	
	def clone_event(self):
		return EyeStrainReminder(self.start_time, self.length, self.user_id)


class EyesCommand(Event):
	def run_event(self, event_queue: EventQueue):
		turning_on = True

		users = []
		with open('eyes_active_users.txt') as active_users:
			for name in active_users:
				users.append(name.strip('\n'))
				if name.strip('\n') == str(self.user_id):
					turning_on = False
			active_users.close()

		if turning_on:
			new_start_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
			reminder_event = EyeStrainReminder(new_start_time, datetime.timedelta(), self.user_id)
			repeated_event = RepeatedEvent(new_start_time, self.length, 1, reminder_event, True, self.user_id, datetime.timedelta(minutes=1))
			event_queue.add(repeated_event)

			with open('eyes_active_users.txt', 'a') as file:
				file.write(str(self.user_id) + '\n')
				file.close()

			event_queue.add(MessageEvent(datetime.datetime.now(), datetime.timedelta(), "Eye Strain Reduction Session Has Begun! Type +eyes To End It.", self.user_id))
		else:
			for i in range(0, len(event_queue.events)):
				if isinstance(event_queue.events[i], RepeatedEvent):
					if isinstance(event_queue.events[i].event, EyeStrainReminder):
						if event_queue.events[i].user_id == self.user_id:
							event_queue.events[i] = NullEvent(datetime.datetime.now(), datetime.timedelta(), self.user_id)
							break

			users.remove(str(self.user_id))
			with open('eyes_active_users.txt', 'w') as file:
				for name in users:
					file.write(name + '\n')
				file.close()

			event_queue.add(MessageEvent(datetime.datetime.now(), datetime.timedelta(), "Eye Strain Reduction Session Has Ended! Type +eyes To Begin Again.", self.user_id))

	def clone_event(self):
		return EyesCommand(self.start_time, self.length, self.user_id)


class PomodoroCommand(Event):
	# This is created when a user runs the "+Pomodoro" command
	def run_event(self, event_queue):
		start_time = datetime.datetime.now() + datetime.timedelta(minutes = 25)
		reminder_event = PomodoroBreakReminder(start_time, datetime.timedelta(), self.user_id)
		repeated_event = PomodoroRepeated(start_time, self.length, 4, reminder_event, self.user_id, datetime.timedelta(minutes= 25))

		start_time_long = datetime.datetime.now() + datetime.timedelta(hours = 2)
		reminder = PomodoroLongBreakReminder(start_time, datetime.timedelta(), self.user_id)
		repeated_long_event = RepeatedEvent(start_time_long, self.length, 1, reminder, True, self.user_id, datetime.timedelta(hours= 2))

		event_queue.add_list([MessageEvent(datetime.datetime.now(), datetime.timedelta(), "Started the Pomodoro Studying method", self.user_id) ,repeated_event, repeated_long_event])

class PomodoroLongBreakReminder(Event):
	reminder_text: str = 'Its time to take a break (30 minutes)'

	def run_event(self, event_queue: EventQueue):
		event_queue.add(MessageEvent(datetime.datetime.now(), datetime.timedelta(), self.reminder_text, self.user_id))
	
	def clone_event(self):
		return PomodoroLongBreakReminder(self.start_time, self.length, self.user_id)


class PomodoroBreakReminder(Event):
	reminder_text: str = 'Its time to take a break (5 minutes)'

	def run_event(self, event_queue: EventQueue):
		event_queue.add(MessageEvent(datetime.datetime.now(), datetime.timedelta(), self.reminder_text, self.user_id))
	
	def clone_event(self):
		return PomodoroBreakReminder(self.start_time, self.length, self.user_id)


class PomodoroRepeated(Event):
	num_of_repeats: int

	unending: bool

	time_interval: int # The amount of time between the repetition of the event

	event: Event # Event to be repeated

	def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, repeats: int, event: Event, user_id, time_interval):
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
		clone.start_time = clone.start_time + self.time_interval + datetime.timedelta(minutes = 5)
		clone.num_of_repeats -= 1
		return clone

		

	def run_event(self, event_queue: EventQueue):
		# Add the wrapped event to the queue to be executed right away
		# Create the next instance of RepeatedEvent and that to the queue

		event_queue.add_list([self.event, MessageEvent(self.start_time + datetime.timedelta(minutes = 5), self.length, "The Break is over", self.user_id) ,self.create_next_repeated_event()])
	
	def clone_event(self):
		return PomodoroRepeated(self.start_time, self.length, self.num_of_repeats, self.event, self.user_id, self.time_interval)


class WaterCommand(Event):
	# This starts the water for the day, reminder after each hour
	def run_event(self, event_queue):
		start_time = datetime.datetime.now() + datetime.timedelta(minutes = 60)
		reminder_event = WaterReminder(start_time, datetime.timedelta(), self.user_id)
		repeated_event = RepeatedEvent(start_time, self.length, 1, reminder_event, True, self.user_id, datetime.timedelta(minutes = 60))

		event_queue.add_list([MessageEvent(datetime.datetime.now(), datetime.timedelta(), "You've setup a hydration reminder for today. You will be reminded every hour to drink water!", self.user_id), repeated_event])


class WaterReminder(Event):
	reminder_text: str = "It's been an hour since you're last water reminder, have you drank your water for the hour?"

	def run_event(self, event_queue: EventQueue):
		event_queue.add(MessageEvent(datetime.datetime.now(), datetime.timedelta(), self.reminder_text, self.user_id))
	
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

		message = "One bottle has just been added to your daily total! You have now drank " + str(num_of_bottles + 1) + " bottle(s) today!"
		event_queue.add(MessageEvent(datetime.datetime.now(), datetime.timedelta(), message, self.user_id))
