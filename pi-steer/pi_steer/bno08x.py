import sys
import time
import pi_steer.log
from board import SCL, SDA
from busio import I2C
from adafruit_bno08x import (
    PacketError,
    # BNO_REPORT_ACCELEROMETER,
    # BNO_REPORT_GYROSCOPE,
    # BNO_REPORT_MAGNETOMETER,
    # BNO_REPORT_LINEAR_ACCELERATION,
    # BNO_REPORT_ROTATION_VECTOR,
    BNO_REPORT_GAME_ROTATION_VECTOR,
    # BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR, 
    # BNO_REPORT_STEP_COUNTER,
    # BNO_REPORT_RAW_ACCELEROMETER,
    # BNO_REPORT_RAW_GYROSCOPE,
    # BNO_REPORT_RAW_MAGNETOMETER,
    # BNO_REPORT_SHAKE_DETECTOR,
    # BNO_REPORT_STABILITY_CLASSIFIER,
    # BNO_REPORT_ACTIVITY_CLASSIFIER, 
    # BNO_REPORT_GYRO_INTEGRATED_ROTATION_VECTOR
)
from adafruit_bno08x.i2c import BNO08X_I2C

# FEATURES = [BNO_REPORT_ACCELEROMETER, BNO_REPORT_GYROSCOPE, BNO_REPORT_MAGNETOMETER, BNO_REPORT_LINEAR_ACCELERATION,
#     BNO_REPORT_ROTATION_VECTOR, BNO_REPORT_GAME_ROTATION_VECTOR, BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR, 
#     BNO_REPORT_STEP_COUNTER, BNO_REPORT_RAW_ACCELEROMETER, BNO_REPORT_RAW_GYROSCOPE, BNO_REPORT_RAW_MAGNETOMETER,
#     BNO_REPORT_SHAKE_DETECTOR, BNO_REPORT_STABILITY_CLASSIFIER, BNO_REPORT_ACTIVITY_CLASSIFIER, 
#     BNO_REPORT_GYRO_INTEGRATED_ROTATION_VECTOR]

FEATURES = [
    BNO_REPORT_GAME_ROTATION_VECTOR,
    ]

BNO_PACKET = BNO_REPORT_GAME_ROTATION_VECTOR

# reset = DigitalOutputDevice('BOARD11', active_high=False, initial_value=True)

BNO085 = [0x4a, 0x4b]

def find_bno085() -> int:
    i2c = I2C(SCL, SDA)
    for address in BNO085:
        try:
            BNO08X_I2C(i2c, address=address)
        except ValueError:
            continue
        return address
    return 0

def now():
    return time.strftime('%X')

def enable_features(bno):
    for feature in FEATURES:
        try:
            bno.enable_feature(feature)
        except Exception as err:
            print(now(), 'BNO085 feature failed:', err)
            return False
    return True

'''
def hard_reset():
    print(now(), 'BNO085 Hard reset')
    reset.on()
    time.sleep(0.1)
    reset.off()
    time.sleep(0.1)
'''

class BNO08X():
    def __init__(self, address, debug) -> None:
        while True:
            try:
                i2c = I2C(SCL, SDA, frequency=400000)
            except Exception as err:
                print('I2C failed', err)
                continue
            time.sleep(0.5)
            break
            
        self.debug = debug
        if debug:
            self.debug_data = pi_steer.log.Log('bno08x data')
            self.debug_euler = pi_steer.log.Log('bno08x euler')
            self.debug_error = pi_steer.log.Log('bno08x error')
        self.i2c = i2c
        self.address = address
        self.bno = None
        self.start()

    def get_bno(self):
        try:
            self.bno = BNO08X_I2C(self.i2c, address=self.address)
        except:
            print(now(), 'BNO085 failed')


    def init(self, i2c, address):
        while True:
            try:
                self.bno.initialize()
            except:
                print(now(), 'First initialization failed, try software hard reset:')
                try:
                    # bno.hard_reset()
                    self.bno.initialize()
                except Exception as err:
                    print(now(), 'BNO085 initialization failed:', err)
                    return
            print(now(), 'BNO085 initialized.')
            return

    def start(self):
        self.get_bno()
        print(now(), 'Init BNO085')
        while True:
            time.sleep(0.1)
            self.init(self.i2c, self.address)
            time.sleep(0.1)
            if not enable_features(self.bno):
                continue
            for discard in range(7):
                try:
                    (qx, qy, qz, qw) = self.search_packet(BNO_PACKET)
                    print('First values:', qx, qy, qz, qw)
                except:
                    pass

            return

    def quaternion(self):
        try:
            # (qx, qy, qz, qw) = self.bno.game_quaternion
            (qx, qy, qz, qw) = self.search_packet(BNO_PACKET)
            if self.debug:
                self.debug_data.log_csv([time.monotonic(), qx, qy, qz, qw])
        except OSError as err:
            print(now(), '\nOSError reading packet', err)
            return None
        except Exception as err:
            print('\nBNO packet read error:', err)
            time.sleep(0.02)
            return None
        return (qw, qx, qy, qz)

    def search_packet(self, id=None):
        processed_count = 0
        while True:
            while self.bno._data_ready:
                try:
                    new_packet = self.bno._read_packet()
                except PacketError as err:
                    print('\nPacket error', err)
                    continue
                packet_report_id = new_packet.data[5]
                try:
                    self.bno._handle_packet(new_packet)
                except Exception as err:
                    print('\npacket handle error', err)
                    # self.bno.soft_reset()
                    enable_features(self.bno)
                    continue
                processed_count += 1
                if id is None:
                    return None
                if packet_report_id == id:
                    data = self.bno._readings[id]
                    return data
           