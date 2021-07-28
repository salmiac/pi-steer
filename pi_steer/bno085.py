import time
from gpiozero import DigitalOutputDevice
from math import atan2, asin, pi, degrees
from board import SCL, SDA
from busio import I2C
from adafruit_bno08x import (
    # BNO_REPORT_ACCELEROMETER,
    # BNO_REPORT_GYROSCOPE,
    # BNO_REPORT_MAGNETOMETER,
    # BNO_REPORT_LINEAR_ACCELERATION,
    BNO_REPORT_ROTATION_VECTOR,
    # BNO_REPORT_GAME_ROTATION_VECTOR,
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
    BNO_REPORT_ROTATION_VECTOR
    ]

reset = DigitalOutputDevice('BOARD11', active_high=False, initial_value=True)

def enable_features(bno):
    for feature in FEATURES:
        try:
            bno.enable_feature(feature)
        except Exception as err:
            print('BNO085 feature failed:', err)

def init():
    print('Init BNO085')
    reset.on()
    time.sleep(0.5)
    reset.off()
    time.sleep(0.5)
    try:
        i2c = I2C(SCL, SDA, frequency=400000)
    except Exception as err:
        print('I2C failed', err)
        return None
    try:
        bno = BNO08X_I2C(i2c, address=0x4b)
    except Exception as err:
        try:
            bno = BNO08X_I2C(i2c, address=0x4a)
        except Exception as err:
            print('BNO085 failed', err)
            return None

    enable_features(bno)
    return bno

class BNO085():
    def __init__(self) -> None:
        self.bno = init()

    def read(self):
        while True:
            try:
                (qx, qy, qz, qw) = self.bno.quaternion
            except:
                time.sleep(1)
                self.bno = init()
                continue
            sinr_cosp = 2 * (qw * qx + qy * qz)
            cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
            roll = degrees(atan2(sinr_cosp, cosr_cosp))

            sinp = 2 * (qw * qy - qz * qx)
            try:
                pitch = asin(sinp)
            except ValueError:
                continue
            pitch = degrees(pitch)

            siny_cosp = 2 * (qw * qz + qx * qy)
            cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
            heading = degrees(atan2(siny_cosp, cosy_cosp))
            if heading < 0:
                heading += 360
            heading = 360 - heading

            return (heading, roll, pitch)