import os
import time
import serial
import numpy as np
import configparser

class scale_serial_conn(object):
    conn = 0
    serial_port_clx = ''
    scale_sett = ''
    serial_baud_rate = ''
    serial_port_name = ''
    timeout = 10
    continuous_read_size = 20
    return_threshold_ratio = 0.05 #5% flactuation to return
    config = ''
    version = 'mouse'

    def __init__(self):
        self.conn = 0
        self.serial_port_name = '/dev/ttyUSB0'
        self.serial_baud_rate = 9600

        ini_path = os.path.join(os.path.expanduser('~'),'.dbconf')
        self.config = configparser.ConfigParser()
        self.config.sections()
        self.config.read(ini_path)
        self.version = self.config['scale']['ver']

    def update_serial_port_name(self,name):
        self.serial_port_name = name

    def update_serial_baud_rate(self,rate):
        self.serial_baud_rate = rate

    def update_timeout(self,tout):
        self.timeout = tout

    def getConnection(self):
        # set-up serial port connection, required before any communication
        self.serial_port_clx = serial.Serial(self.serial_port_name,self.serial_baud_rate,timeout=self.timeout)
        print("connected with the port "+self.serial_port_clx.name)
        self.conn = 1

    def read_scale_based_on_setting(self):
        if self.version == 'rat':
            data = self.read_decode_continuous_weight_data()
        elif self.version == 'mouse':
            data = self.read_decode_continuous_stable_weight_data()
        
        return data

    def read_decode_continuous_stable_weight_data(self):
        self.serial_port_clx.flushInput()
        data_recv = self.serial_port_clx.readline() #first line, dircard

        loop_timeout = time.time() + self.timeout   # set timeout for the loop
        weight_readout = 0
        while True:
            # receive a new data
            data_recv = self.serial_port_clx.readline()
            data_recv = data_recv.decode()

            # decode and convert to float
            if len(data_recv) > 10:
                if data_recv[0:2] == 'ST': #this for the mice scale, got a stable reading
                    weight_readout = float(data_recv[6:17])#extracting reading
                    if weight_readout > 3: # need to be at least 3 grams, aviod false reading
                        break
                    else:
                        weight_readout = 0

            if time.time() > loop_timeout:
                break
            
        return weight_readout

    def read_decode_continuous_weight_data(self):
        self.serial_port_clx.flushInput()
        data_recv = self.serial_port_clx.readline() #first line, dircard

        ii = 0
        weight_readings = np.zeros(self.continuous_read_size)

        while True:
            # receive a new data
            data_recv = self.serial_port_clx.readline()
            data_recv = data_recv.decode()

            # decode and convert to float
            if len(data_recv) > 10:
                if data_recv[0:2] == 'SU': #this for the rat scale (kern)
                    weight_readout = float(data_recv[8:15])#extracting reading
            
                    # save in the array
                    weight_readings[ii] = weight_readout

                    ii += 1
                    if ii > (self.continuous_read_size-1):
                        ii = 0
                
                    # compute retuning threshold
                    if np.any(weight_readings<10): # data not been filled full yet
                        working_thredhold = -1 # unreachable threshold
                    else:
                        working_thredhold = np.max(weight_readings)*self.return_threshold_ratio
                
                    # must go smaller than the threshold to return
                    if (np.max(weight_readings)-np.min(weight_readings))<working_thredhold:
                        break
        
        return np.mean(weight_readings)
    
    def decode_wait_recv_weight_reading(self):
        data_recv = self.serial_port_clx.readline()
        data_recv = data_recv.decode()

        weight_readout = 0
        if len(data_recv) > 10:
            if data_recv[0:2] == 'GS':
                weight_readout = float(data_recv[2:14])#extracting reading
            
        # it might have several different lines ahead of real signal, so there might still have signal ahead
        if weight_readout < 1:#weight = 0, try to read more command
            time.sleep(0.1)
            while self.serial_port_clx.in_waiting:
                data_recv = self.serial_port_clx.readline()
                data_recv = data_recv.decode()

                if len(data_recv) > 10:
                    if data_recv[0:2] == 'GS':
                        weight_readout = float(data_recv[2:14])#extracting reading
                        break

        self.serial_port_clx.flushInput()  
        return weight_readout


    def decode_current_weight_reading(self):
        # decode current weight reading which have already be sent
        # need to make sure have message received
        # can be check from ctx.serial_port_clx.in_waiting
        weight_readout = 0
        while self.serial_port_clx.in_waiting:
            data_recv = self.serial_port_clx.readline()
            data_recv = data_recv.decode()

            if len(data_recv) > 10:
                if data_recv[0:2] == 'GS':
                    weight_readout = float(data_recv[2:14])#extracting reading
                    break
        self.serial_port_clx.flushInput()
        return weight_readout


    def receive_decode_weight_reading(self):
        # wait and read weight reading 
        # will try to read every second until timeout reaches
        for x in range(0, self.timeout):
            data_recv = ''
            weight_readout = 0
            if self.serial_port_clx.in_waiting:  # Or: while ser.inWaiting():
                data_recv = self.serial_port_clx.readline()
                data_recv = data_recv.decode()
                x = 1 #will do more loop once we got data
            else:
                time.sleep(1) # got nothing, wait for 1s to re-read
            if len(data_recv) > 10:
                if data_recv[0:2] == 'GS':
                    weight_readout = float(data_recv[2:14])#extracting reading
                    break
        self.serial_port_clx.flushInput()
        return weight_readout

    def close_conn(self):
        # distroy serial port connection
        self.serial_port_clx.close()
        self.conn = 0
            
    def __del__(self):
        if self.conn == 1:
            self.close_conn()


if __name__ == "__main__":
    ctx = scale_serial_conn()
    ctx.getConnection()
    try:
        while True:
            weight_reading = ctx.receive_decode_weight_reading()
            if weight_reading > 0:
                print("weight reading received: " + str(weight_reading)+"g")
    except KeyboardInterrupt:
            print("exiting")
            ctx.close_conn()

