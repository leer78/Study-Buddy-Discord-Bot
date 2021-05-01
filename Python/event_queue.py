import datetime
from Python.events import Event

class EventQueue:
	# The events sorted decreasing order of the timedelta from the current time
	events: list[Event]

	def __init__(self):
		self.events = []

	def add(self, event: Event):
		self.events.append(event)

		self.events.sort(key= lambda e: e.start_time - datetime.datetime.now(), reversed=True)
	
	def add_list(self, new_events: list[Event]):
		for e in new_events:
			self.events.append(e)
		
		self.events.sort(key= lambda e: e.start_time - datetime.datetime.now())

	def pop(self):
		return self.events.pop()


	def is_ready(self) -> bool:
		if len(self.events) == 0:
			return False
		
		if self.events[len(self.events) - 1].start_time - datetime.datetime.now() <= datetime.timedelta():
			return True
		
		return False

	def view(self):
		return events