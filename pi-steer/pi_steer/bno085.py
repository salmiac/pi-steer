import time
import signal
from gpiozero import DigitalOutputDevice
from math import atan2, asin, pi, degrees
from board import SCL, SDA
from busio import I2C
from adafruit_bno08x import (
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

AVG = 5

reset = DigitalOutputDevice('BOARD11', active_high=False, initial_value=True)

def timeout(signum, frame):
    raise Exception('Timeout')

signal.signal(signal.SIGALRM, timeout)

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

def hard_reset():
    print(now(), 'BNO085 Hard reset')
    reset.on()
    time.sleep(0.1)
    reset.off()
    time.sleep(0.1)

def init(i2c):
    while True:
        try:
            print(now(), 'BNO085 try I2C address 0x4a')
            bno = BNO08X_I2C(i2c, address=0x4a)
        except:
            try:
                print(now(), 'BNO085 try I2C address 0x4b')
                bno = BNO08X_I2C(i2c, address=0x4b)
            except:
                print(now(), 'BNO085 failed')
                time.sleep(1)
                hard_reset()
                continue

        try:
            bno.initialize()
        except:
            print(now(), 'First initialization failed, try software hard reset:')
            try:
                bno.hard_reset()
                bno.initialize()
            except Exception as err:
                print(now(), 'BNO085 initialization failed:', err)
                return None

        print(now(), 'BNO085 initialized.')
        return bno

class BNO085():
    def __init__(self) -> None:
        self.last_heading = None
        self.heading_reference = 0
        self.last_roll = 0
        self.bno = self.start()

    def start(self):
        print(now(), 'Init BNO085')
        while True:
            try:
                i2c = I2C(SCL, SDA, frequency=100000)
            except Exception as err:
                print(now(), 'I2C failed', err)
                return None
            time.sleep(0.2)
            bno = init(i2c)
            if not bno:
                hard_reset()
                continue
            if not enable_features(bno):
                hard_reset()
                continue
            if self.last_heading is not None:
                self.heading_reference = (self.heading_reference + self.last_heading) % 360
            return bno

    def read_single(self):
        read_counter = 0
        reset_counter = 0
        value_counter = 0
        heading_counter = 0
        while True:
            if read_counter:
                print(now(), 'BNO085 Read retry: ', read_counter)
            if reset_counter:
                print(now(), 'BNO085 Reset retry: ', reset_counter)
            if value_counter:
                print(now(), 'BNO085 value error: ', value_counter)
            if heading_counter:
                print(now(), 'BNO085 heading retry: ', heading_counter)
            if self.bno is None:
                time.sleep(1)
                self.bno = self.start()
                continue
            read_counter += 1
            # signal.alarm(1)
            try:
                (qx, qy, qz, qw) = self.bno.game_quaternion
            except:
                # signal.alarm(0)
                time.sleep(0.02)
                if read_counter < 3:
                    continue

                read_counter = 0
                reset_counter += 1

                if reset_counter < 3:
                    print(now(), 'BNO085 try soft reset\n')
                    try:
                        self.bno.soft_reset()
                        print(now(), 'BNO085 soft reset done\n')
                    except:
                        print(now(), 'Soft reset failed\n')
                    self.bno = None
                    continue
                hard_reset()
                self.bno = None
                time.sleep(0.5)
                continue
            # signal.alarm(0)

            read_counter = 0
            reset_counter = 0
            sinr_cosp = 2 * (qw * qx + qy * qz)
            cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
            roll = degrees(atan2(sinr_cosp, cosr_cosp))

            sinp = 2 * (qw * qy - qz * qx)
            try:
                pitch = asin(sinp)
            except ValueError:
                value_counter += 1
                print(now(), 'Value error:', qx, qy, qz, qw )
                time.sleep(0.01)
                continue
            value_counter = 0
            pitch = degrees(pitch)

            siny_cosp = 2 * (qw * qz + qx * qy)
            cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
            heading = -degrees(atan2(siny_cosp, cosy_cosp))
            heading = (heading + self.heading_reference) % 360
            # if self.last_heading is not None and abs(self.last_heading - heading) > 30 and heading_counter < 3:
            #     heading_counter += 1
            #     time.sleep(0.1)
            #     continue
            heading_counter = 0
            self.last_heading = heading
 
            return (heading, roll, pitch)

    def read(self):
        
        # for n in range(AVG):
        return self.read_single()
