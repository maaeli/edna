import PyTango
import time

class CB:
	def push_event(self, event):
		print event.attr_value.value

dev=PyTango.DeviceProxy("dau/edna/1")

cb=CB()
dev.subscribe_event("jobSuccess", PyTango.EventType.CHANGE_EVENT, cb, [], True) 

time.sleep(5000)
