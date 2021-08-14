import time
from board import SCL, SDA
from busio import I2C

def get_i2c():
    while True:
        try:
            i2c = I2C(SCL, SDA, frequency=400000)
        except Exception as err:
            print(time.strftime('%X'), 'I2C failed', err)
            time.sleep(1)
            continue
        return i2c
