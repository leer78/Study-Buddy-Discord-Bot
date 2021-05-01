import datetime
from events import Event

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


