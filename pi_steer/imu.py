import time
import board
import busio
import adafruit_bno055
import pi_steer.automation_hat
import socket
import struct
import sys
import binascii
import json
import pi_steer.automation_hat as hat

ROLL_FILTER_WINDOW_SIZE = 1800 * 100
HEADING_FILTER_WINDOW_SIZE = 10

class IMU():
    def __init__(self):
        # Use these lines for I2C
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.imu = adafruit_bno055.BNO055_I2C(self.i2c)
        time.sleep(0.1) # short pause after ads1015 class creation recommended
        
        print("Accelerometer (m/s^2): {}".format(self.imu.acceleration))
        print("Magnetometer (microteslas): {}".format(self.imu.magnetic))
        print("Gyroscope (rad/sec): {}".format(self.imu.gyro))
        print("Euler angle: {}".format(self.imu.euler))
        print("Quaternion: {}".format(self.imu.quaternion))
        print("Linear acceleration (m/s^2): {}".format(self.imu.linear_acceleration))
        print("Gravity (m/s^2): {}".format(self.imu.gravity))
        print("Analog1: {}".format(hat.analog1()))

        self.heading = 0
        self.roll = 0
        self.headings = []
        self.rolls = []
        self.heading_sum = 0
        self.roll_sum = 0
    
    def get_heading_and_roll(self):
        (heading, roll, yawn) = self.imu.euler
        if heading is not None and heading >= 0 and heading <= 360:
            self.headings.append(heading)
            self.heading_sum += heading
            if len(self.headings) > HEADING_FILTER_WINDOW_SIZE:
                self.heading_sum -= self.headings[0]
                del self.headings[0]
            self.heading = self.heading_sum / len(self.headings)
        if roll is not None and roll >= -90 and roll <= 90:
            self.rolls.append(roll)
            self.roll_sum += roll
            if len(self.rolls) > ROLL_FILTER_WINDOW_SIZE:
                self.roll_sum -= self.rolls[0]
                del self.rolls[0]
            self.roll = self.roll_sum / len(self.rolls)
        return self.heading, self.roll
