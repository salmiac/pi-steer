import sys
import time
import pi_steer.log
import serial
import struct
import threading

class BNO08X():
    def __init__(self, debug):
        self.uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=0.1)
        self.debug = debug
        self.orientation = (0,0,0)
        self.lock = threading.Lock()
        self.reader_thread = threading.Thread(target=self.reader)

    def read(self):
        header = False
        for n in range(50):
            data = self.uart.read(1)
            if self.debug:
                print(data)
            if len(data) == 0:
                continue
            if data[0] == 0xaa:
                if header:
                    data = self.uart.read(17)
                    if self.debug:
                        print(data)
                    if data is not None and len(data) == 17:
                        (
                            index,
                            heading,
                            pitch,
                            roll,
                            acc_x,
                            acc_y,
                            acc_z,
                            mi,
                            mr,
                            res,
                            csum
                        ) = struct.unpack_from("<BhhhhhhBBBB", data)
                        if csum != sum(data[0:16]) % 256:
                            return None
                        return heading*0.01, roll*0.01, pitch*0.01
                else:
                    header = True
            else:
                header = False
    
    def get_orientation(self):
        self.lock.acquire()
        (heading, roll, pitch) = self.orientation
        self.lock.release()
        return (heading, roll, pitch)

    def reader(self):
        while True:
            data = self.read()
            if data is not None:
                (heading, roll, pitch) = data
                if heading is not None:
                    self.lock.acquire()
                    self.orientation = (heading, roll, pitch)
                    if self.debug:
                        print(self.orientation)
                    self.lock.release()
