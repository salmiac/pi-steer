import time
import struct
import pi_steer.debug as db
import smbus2

CONFIG_MODE = 0x00
ACCONLY_MODE = 0x01
MAGONLY_MODE = 0x02
GYRONLY_MODE = 0x03
ACCMAG_MODE = 0x04
ACCGYRO_MODE = 0x05
MAGGYRO_MODE = 0x06
AMG_MODE = 0x07
IMUPLUS_MODE = 0x08

_POWER_NORMAL = 0x00
_POWER_LOW = 0x01
_POWER_SUSPEND = 0x02

_MODE_REGISTER = 0x3D
_PAGE_REGISTER = 0x07
_ACCEL_CONFIG_REGISTER = 0x08
_MAGNET_CONFIG_REGISTER = 0x09
_GYRO_CONFIG_0_REGISTER = 0x0A
_GYRO_CONFIG_1_REGISTER = 0x0B
_QUATERNION_REGISTER = 0x20
_CALIBRATION_REGISTER = 0x35
_OFFSET_ACCEL_REGISTER = 0x55
_OFFSET_MAGNET_REGISTER = 0x5B
_OFFSET_GYRO_REGISTER = 0x61
_RADIUS_ACCEL_REGISTER = 0x67
_RADIUS_MAGNET_REGISTER = 0x69
_TRIGGER_REGISTER = 0x3F
_POWER_REGISTER = 0x3E
_ID_REGISTER = 0x00
# Axis remap registers and values
_AXIS_MAP_CONFIG_REGISTER = 0x41
_AXIS_MAP_SIGN_REGISTER = 0x42

class BNO055():
    def __init__(self, address, debug=False):
        self.i2c = smbus2.SMBus(1)
        self.address = address 
        self.debug = debug

        time.sleep(0.1)
        device_id = int(self.i2c.read_byte_data(self.address, _ID_REGISTER))
        if debug:
            db.write('ID {}'.format(device_id))
        if device_id == 0xa0:
            self._write_config(_MODE_REGISTER, CONFIG_MODE)
            self._write_config(_POWER_REGISTER, _POWER_NORMAL)
            self._write_config(_MODE_REGISTER, IMUPLUS_MODE)
            if debug:
                db.write('Power {}'.format(self.i2c.read_byte_data(self.address, _POWER_REGISTER)) )
                db.write('Mode {}'.format(self.i2c.read_byte_data(self.address, _MODE_REGISTER)) )

        else:
            if debug:
                db.write('Not BNO055 ID!')
            self.i2c_address = 0

    def _write_config(self, register, value):
        time.sleep(0.02)
        self.i2c.write_i2c_block_data(self.address, register, [value])
        time.sleep(0.1)


    def _read(self, address, register, length=1):
        return self.i2c.read_i2c_block_data(address, register, length)

    def quaternion(self):
        if self.address:
            scale = 1.0 / (1 << 14)
            return tuple(scale * value for value in struct.unpack('<hhhh', bytes(self._read(self.address, _QUATERNION_REGISTER, 8))))

