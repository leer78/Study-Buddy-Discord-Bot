import datetime
from events import Event

class EventQueue:
	# The events sorted increasing order of the timedelta from the current time
	events: list[Event]

	def __init__(self):
		self.events = []

	def add(self, event: Event):
		self.events.append(event)

		self.events.sort(key= lambda e: e.start_time - datetime.datetime.now())


def sorting_key(e: Event):
	return e.start_time - datetime.datetime.now()