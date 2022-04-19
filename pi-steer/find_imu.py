from audioop import add
import time
import struct
import pi_steer.debug as db
import smbus2

from board import SCL, SDA
from busio import I2C
from adafruit_bno08x.i2c import BNO08X_I2C

BNO055 = [0x28, 0x29]
BNO085 = [0x4a, 0x4b]

def find_bno055() -> int:
    for address in BNO055:
        try:
            smbus2.SMBus(1).read_byte_data(address, 0)
        except OSError:
            continue
        return address
    return 0

def find_bno085() -> int:
    i2c = I2C(SCL, SDA)
    for address in BNO085:
        try:
            BNO08X_I2C(i2c, address=address)
        except ValueError:
            continue
        return address
    return 0

address = find_bno085()
if address:
    print('BNO085', hex(address))

address = find_bno055()
if address:
    print('BNO055', hex(address))


