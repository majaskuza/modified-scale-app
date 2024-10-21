import json
import time
from datetime import datetime
from helpers import zmqhelper

class zmq_messenger(object):
    zmq_conn = False
    zmq_pusher = ''

    def __init__(self):
        self.zmq_conn = False

    def getPusherConnection(self):
        self.zmq_pusher = zmqhelper.pusher()
        self.zmq_conn = True

    def start_session(self,subjid,rigid):
        now = datetime.now()
        current_ts = now.strftime("%Y-%m-%d_%H:%M:%S")
        msg = json.dumps({'event':'start_session','subjid':subjid,'ts':current_ts})
        self.zmq_pusher.send_string(f'{rigid}_startsession {msg}')
        time.sleep(0.2)
        self.zmq_pusher.send_string(f'{rigid}_startsession {msg}')
        time.sleep(0.2)
        self.zmq_pusher.send_string(f'{rigid}_startsession {msg}')


