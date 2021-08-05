import board
import busio
import time
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode

def init():
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        ads.mode = Mode.CONTINUOUS
        return ads
    except:
        return None

ads = init()

while True:
    try:
        chan = AnalogIn(ads, ADS.P0)
    except:
        time.sleep(0.1)
        continue

    print('\r', chan.value, chan.voltage, end='')

    time.sleep(0.01)
