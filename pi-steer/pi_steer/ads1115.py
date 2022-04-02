import time
import time
import struct
import smbus
import pi_steer.debug as db

_CONVERSION_REGISTER = 0x00
_CONFIG_REGISTER = 0x01
_CONFIGURATION = 0b0100_0100_1010_0011

class ADS1115():
    def __init__(self, address, debug=False):
        self.i2c = smbus.SMBus(1)
        self.address = address 
        self.debug = debug

        self.i2c.write_i2c_block_data(self.address, _CONFIG_REGISTER, bytearray([0b0100_0010, 0b1010_0011]))
        time.sleep(0.1)
        if debug:
            db.write('ADS1115 configuration {}'.format(self.i2c.read_i2c_block_data(self.address, _CONFIG_REGISTER, 2)))

    def read(self):
        data = self.i2c.read_i2c_block_data(self.address, _CONVERSION_REGISTER, 2)
        return struct.unpack('>h', data )[0]
