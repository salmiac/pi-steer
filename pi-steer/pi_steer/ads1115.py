from board import SCL, SDA
from busio import I2C
import time
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode

def init(i2c):
    print('Init ADS1115')

    try:
        ads = ADS.ADS1115(i2c)
        ads.mode = Mode.CONTINUOUS
    except Exception as err:
        print('ADS1115 failed', err)
        return None
    return ads

class ADS1115():
    def __init__(self):
        while True:
            try:
                i2c = I2C(SCL, SDA, frequency=40000)
            except Exception as err:
                print('I2C failed', err)
                continue
            break

        self.ads = init(i2c)
        self.i2c = i2c

    def read(self):
        while True:
            try:
                chan = AnalogIn(self.ads, ADS.P0)
            except Exception as err:
                print('ADS1115 Read failed', err)
                time.sleep(0.01)
                self.ads = init(self.i2c)
                continue
        
            return chan.voltage
