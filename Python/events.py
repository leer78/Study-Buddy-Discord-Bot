import datetime
import time
import discord
from event_queue import EventQueue


class Event:
	user_id: discord.User

	start_time: datetime.time
	length: datetime.timedelta
	end_time: datetime.time


	def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, user_id: discord.User):
		self.user_id = user_id

		self.start_time = start_time
		self.length = length

		self.end_time = self.start_time + self.length
	

	def run_event(self, event_queue: EventQueue):
		raise NotImplementedError

	def clone_event(self) -> Event:
		raise NotImplementedError


class RepeatedEvent(Event):
	num_of_repeats: int

	unendeding: bool 

	time_interval: int # The amount of time between the repetition of the event

	event: Event # Event to be repeated

	def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, repeats: int, event: Event, unending: bool):
		super().__init__(start_time, length, )
		self.num_of_repeats = repeats
		self.event = event
		self.unendeding = unending

	def create_next_repeated_event(self) -> Event:
		new_event = self.event.clone_event()
		new_event.start_time = new_event.start_time + self.time_interval
		
		if self.unendeding:
			return RepeatedEvent(start_time=self.start_time + self.time_interval, repeats=1, event=new_event, unending=self.unendeding)
		
		if self.num_of_repeats == 0:
			return NullEvent(datetime.datetime.now(), datetime.timedelta(), self.user_id)

		return RepeatedEvent(start_time=self.start_time + self.time_interval, length=self.length, repeats=self.num_of_repeats - 1, event=new_event, unending=self.unendeding)

	def run_event(self, event_queue: EventQueue):
		# Add the wrapped event to the queue to be executed right away
		# Create the next instance of RepeatedEvent and that to the queue
		event_queue.add([self.event, self.create_next_repeated_event()])
	
	def clone_event(self):
		return RepeatedEvent(self.start_time, self.length, self.num_of_repeats, self.event, self.unendeding)



class NullEvent(Event):

	def run_event(self, event_queue):
		return None

class MessageEvent(Event):

	message_content: str

	def __init__(self, start_time: datetime.datetime, length: datetime.timedelta, message: str):
		super().__init__(start_time, length)
		self.message_content = message

	def run_event(self, event_queue):
		return self.message_content
	
	def clone_event(self):
		return MessageEvent(self.start_time, self.length, self.message_content)