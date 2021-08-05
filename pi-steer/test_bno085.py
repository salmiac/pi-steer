import time
from math import atan2, asin, pi, degrees
from board import SCL, SDA
from busio import I2C
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER, BNO_REPORT_GYROSCOPE, BNO_REPORT_MAGNETOMETER, BNO_REPORT_LINEAR_ACCELERATION,
    BNO_REPORT_ROTATION_VECTOR, BNO_REPORT_GAME_ROTATION_VECTOR, BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR, 
    BNO_REPORT_STEP_COUNTER, BNO_REPORT_RAW_ACCELEROMETER, BNO_REPORT_RAW_GYROSCOPE, BNO_REPORT_RAW_MAGNETOMETER,
    BNO_REPORT_SHAKE_DETECTOR, BNO_REPORT_STABILITY_CLASSIFIER, BNO_REPORT_ACTIVITY_CLASSIFIER, 
    BNO_REPORT_GYRO_INTEGRATED_ROTATION_VECTOR
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


def enable_features(bno):
    for feature in FEATURES:
        try:
            bno.enable_feature(feature)
        except Exception as err:
            print('BNO085 feature failed:', err)

def init():
    print('Init BNO085')
    try:
        i2c = I2C(SCL, SDA, frequency=400000)
        bno = BNO08X_I2C(i2c, address=0x4b)
    except Exception as err:
        print('BNO085 I2C failed', err)
        return (None, None)

    enable_features(bno)
    return (i2c, bno)

(i2c, bno) = init()

while True:
    try:
        (qx, qy, qz, qw) = bno.quaternion
    except:
        time.sleep(1)
        (ic2, bno) = init()
        continue
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll = degrees(atan2(sinr_cosp, cosr_cosp))

    sinp = 2 * (qw * qy - qz * qx)
    try:
        pitch = asin(sinp)
    except ValueError:
        print('\n',qx, qy, qz, qw,'\n')
        pitch = pi/2
    pitch = degrees(pitch)

    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    heading = degrees(atan2(siny_cosp, cosy_cosp))
    if heading < 0:
        heading += 360

    print('\r H {: = 7.2f} P {: = 7.2f} R {: = 7.2f}'.format(heading, pitch, roll), end='')

    time.sleep(0.1)

