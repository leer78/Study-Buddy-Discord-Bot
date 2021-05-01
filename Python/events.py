import datetime
import time
import discord


class Event:
	user_id: discord.User

	start_time: datetime.time
	length: datetime.timedelta
	end_time: datetime.time


	def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, user_id: int):
		self.user_id = user_id

		self.start_time = start_time
		self.length = length

		self.end_time = self.start_time + self.length
	

	def run_event(self, event_queue):
		raise NotImplementedError

	def clone_event(self) -> Event:
		raise NotImplementedError


class NullEvent(Event):

	def run_event(self, event_queue):
		return None

class RepeatedEvent(Event):
	num_of_repeats: int

	time_interval: int # The amount of time between the repetition of the event

	event: Event # Event to be repeated

	def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, repeats: int, event: Event):
		super().__init__(start_time, length, )
		self.num_of_repeats = repeats
		self.event = event
	
	def create_next_repeated_event(self) -> Event:
		if self.num_of_repeats == 0:
			return NullEvent(datetime.datetime.now(), datetime.timedelta(), self.user_id)

		new_event = self.event.clone_event()
		new_event.start_time = new_event.start_time + self.time_interval

		return RepeatedEvent(start_time=self.start_time + self.time_interval, length=self.length, repeats=self.num_of_repeats - 1, event=new_event)

	def run_event(self, event_queue):
		# Add the wrapped event to the queue to be executed right away
		event_queue.add(self.event)

		# Create the next instance of RepeatedEvent and that to the queue
		event_queue.add(self.create_next_repeated_event())




class MessageEvent(Event):

	message_content: str

	def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, message: str):
		super().__init__(start_time, length)
		self.message_content = message

	def run_event(self, event_queue):
		return self.message_content