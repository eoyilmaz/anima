import threading
import time

class run(object):
	def __init__(self):
		self.lock = threading.Lock()
		self.abc()

	def ipBul(self):
		print("1")
