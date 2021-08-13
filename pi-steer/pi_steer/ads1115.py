from board import SCL, SDA
from busio import I2C
import time
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode

def init():
    print('Init ADS1115')
    try:
        i2c = I2C(SCL, SDA, frequency=100000)
    except Exception as err:
        print('I2C failed', err)
        return None

    try:
        ads = ADS.ADS1115(i2c)
        ads.mode = Mode.CONTINUOUS
    except Exception as err:
        print('ADS1115 failed', err)
        return None
    return ads

class ADS1115():
    def __init__(self):
        self.ads = init()

    def read(self):
        while True:
            try:
                chan = AnalogIn(self.ads, ADS.P0)
            except Exception as err:
                print('ADS1115 Read failed', err)
                time.sleep(0.01)
                self.ads = init()
                continue
        
            return chan.voltage
