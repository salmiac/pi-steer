import math
import time
import signal
import pi_steer.log
from gpiozero import DigitalOutputDevice
from math import atan2, asin, pi, degrees
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
AVG = 3
AVG_DIFF = 0.05

reset = DigitalOutputDevice('BOARD11', active_high=False, initial_value=True)

def timeout(signum, frame):
    raise Exception('Timeout')

signal.signal(signal.SIGALRM, timeout)

def what(a, b):
    print('slices', a,b)

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

class BNO08X():
    def __init__(self, debug) -> None:
        while True:
            try:
                i2c = I2C(SCL, SDA, frequency=40000)
            except Exception as err:
                print('I2C failed', err)
                continue
            break
            
        self.debug = debug
        if debug:
            self.debug_data = pi_steer.log.Log('bno08x data')
            self.debug_error = pi_steer.log.Log('bno08x error')
        self.i2c = i2c
        self.last_heading = None
        self.heading_reference = 0
        self.last_roll = 0
        self.start()

    def start(self):
        print(now(), 'Init BNO085')
        while True:
            time.sleep(0.1)
            bno = init(self.i2c)
            bno.initialize()
            time.sleep(0.1)
            if not bno:
                hard_reset()
                continue
            if not enable_features(bno):
                hard_reset()
                continue
            if self.last_heading is not None:
                self.heading_reference = self.last_heading
            self.bno = bno
            for discard in range(7):
                try:
                    (qx, qy, qz, qw) = self.search_packet(BNO_PACKET)
                except:
                    pass
                print('First values:', qx, qy, qz, qw)

            return

    def read_single(self):
        read_counter = 0
        reset_counter = 0
        value_counter = 0
        while True:
            if read_counter:
                print(now(), 'BNO085 Read retry: ', read_counter)
            if reset_counter:
                print(now(), 'BNO085 Reset retry: ', reset_counter)
            if value_counter:
                pass
                # print(now(), 'BNO085 value error: ', value_counter)
            if self.bno is None:
                time.sleep(1)
                self.start()
                continue
            read_counter += 1
            # signal.alarm(1)
            try:
                # (qx, qy, qz, qw) = self.bno.game_quaternion
                (qx, qy, qz, qw) = self.search_packet(BNO_PACKET)
                if self.debug:
                    self.debug_data.log_csv([time.monotonic(), qx, qy, qz, qw])
            except Exception as err:
                print('BNO packet read error:', err)
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
                time.sleep(0.1)
                continue
            # signal.alarm(0)

            read_counter = 0
            reset_counter = 0
            if abs(qw) > 1 or abs(qx) > 1 or abs(qy) > 1 or abs(qz) > 1:
                value_counter += 1
                # print(now(), 'Value error:', qx, qy, qz, qw )
                # time.sleep(0.01)
                continue
            value_counter = 0
            norm = math.sqrt(qw*qw + qx*qx + qy*qy + qz*qz)
            if norm == 0:
                continue
 
            return (qx/norm, qy/norm, qz/norm, qw/norm)

    def read(self):
        while True:
            sum_qx = 0
            sum_qy = 0
            sum_qz = 0
            sum_qw = 0
            for n in range(AVG):
                (qx, qy, qz, qw) = self.read_single()
                if n:
                    dx = sum_qx/n - qx
                    dy = sum_qy/n - qy
                    dz = sum_qz/n - qz
                    dw = sum_qw/n - qw
                    diff = math.sqrt(dx*dx + dy*dy + dz*dz + dw*dw)
                    # print('Diff', diff)
                    if diff > AVG_DIFF:
                        print('Unreliable value', dx, dy, dz, dw)
                        continue
                sum_qx += qx
                sum_qy += qy
                sum_qz += qz
                sum_qw += qw
            qx = sum_qx / AVG
            qy = sum_qy / AVG
            qz = sum_qz / AVG
            qw = sum_qw / AVG
            
            sinr_cosp = 2 * (qw * qx + qy * qz)
            cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
            roll = degrees(atan2(sinr_cosp, cosr_cosp))

            sinp = 2 * (qw * qy - qz * qx)
            try:
                pitch = asin(sinp)
            except ValueError:
                print(now(), 'Value error:', qx, qy, qz, qw )
                time.sleep(0.01)
                continue
            pitch = degrees(pitch)

            siny_cosp = 2 * (qw * qz + qx * qy)
            cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
            heading = -degrees(atan2(siny_cosp, cosy_cosp))
            heading = (heading + self.heading_reference) % 360
            self.last_heading = heading

            return (heading, roll, pitch)


    def search_packet(self, id=None):
        processed_count = 0
        while True:
            while self.bno._data_ready:
                try:
                    new_packet = self.bno._read_packet()
                except PacketError as err:
                    print('Packet error', err)
                    continue
                packet_report_id = new_packet.data[5]
                try:
                    self.bno._handle_packet(new_packet)
                except Exception as err:
                    print('packet handle error', err)
                    continue
                processed_count += 1
                if id is None:
                    return None
                if packet_report_id == id:
                    data = self.bno._readings[id]
                    return data
            time.sleep(0.001)
           