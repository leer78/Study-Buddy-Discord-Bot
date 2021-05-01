import datetime
import time
import discord


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
	# This is created when a user runs the "+eyes" command
	def run_event(self, event_queue: EventQueue):
		turning_on = True

		users = []
		with open('../Database/eyes_active_users.txt') as active_users:
			for name in active_users:
				users.append(name)
				if name == str(self.user_id):
					turning_on = False
			active_users.close()

		if turning_on:
			new_start_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
			reminder_event = EyeStrainReminder(new_start_time, datetime.timedelta(), self.user_id)
			repeated_event = RepeatedEvent(new_start_time, self.length, 1, reminder_event, False, self.user_id, datetime.timedelta(minutes=1))
			event_queue.add(repeated_event)

			with open('../Database/eyes_active_users.txt', 'a') as file:
				file.write(str(self.user_id))
				file.close()
		else:
			for event in event_queue.events:
				if isinstance(event, RepeatedEvent):
					if isinstance(event.event, EyeStrainReminder):
						if event.user_id == self.user_id:
							event_queue.remove(event)
							break
			users.remove(str(self.user_id))
			with open('../Database/eyes_active_users.txt', 'w') as file:
				for name in users:
					file.write(name)

	def clone_event(self):
		return EyesCommand(self.start_time, self.length, self.user_id)

