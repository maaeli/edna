from PyTango import *
import time

class cb (object):
    def push_event(self, event):
        print event


callback = cb()
dev=DeviceProxy("dau/edna/2")
print "Imported!"

ev_id = dev.subscribe_event ("jobSuccess", EventType.CHANGE_EVENT, callback, [], False)

time.sleep(30)

