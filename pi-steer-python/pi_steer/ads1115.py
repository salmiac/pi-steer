import time
import time
import struct
import smbus2
import pi_steer.debug as db

_CONVERSION_REGISTER = 0x00
_CONFIG_REGISTER = 0x01
_CONFIGURATION = 0b0101_0100_1010_0011

class ADS1115():
    def __init__(self, address, debug=False):
        self.i2c = smbus2.SMBus(1)
        self.address = address 
        self.debug = debug

        self.i2c.write_i2c_block_data(self.address, _CONFIG_REGISTER, [0b1100_0001, 0b1000_0011])
        time.sleep(0.1)
        if debug:
            db.write('ADS1115 configuration {}'.format(self.i2c.read_i2c_block_data(self.address, _CONFIG_REGISTER, 2)))

    def read(self):
        self.i2c.write_i2c_block_data(self.address, _CONFIG_REGISTER, [0b1100_0000, 0b1000_0011])
        data = self.i2c.read_i2c_block_data(self.address, _CONVERSION_REGISTER, 2)
        return struct.unpack('>h', bytes(data) )[0]
