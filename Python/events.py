import datetime
import time


class Event:
	event_id: int

	start_time: datetime.time
	length: datetime.timedelta
	end_time: datetime.time

	repeated: bool

	def __init__(self, start_time, length):
		self.start_time = start_time
		self.length = length

		self.end_time = self.start_time + self.length
	

	def run_event(self):
		raise NotImplementedError
		

class MessageEvent(Event):

	message_content: str

	def run_event(self):
		return self.message_content