import time
import math
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
        time.sleep(1) # short pause after ads1015 class creation recommended
        
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
        self.headingsx = []
        self.headingsy = []
        self.rolls = []
        self.headingx_sum = 0
        self.headingy_sum = 0
        self.roll_sum = 0
    
    def get_heading_and_roll(self):
        (heading, roll, yawn) = self.imu.euler
        if heading is not None and heading >= 0 and heading <= 360:
            heading_rad = math.radians(heading)
            headingx = math.sin(heading_rad)
            headingy = math.cos(heading_rad)
            self.headingsx.append(headingx)
            self.headingsy.append(headingy)
            self.headingx_sum += headingx
            self.headingy_sum += headingy
            if len(self.headingsx) > HEADING_FILTER_WINDOW_SIZE:
                self.headingx_sum -= self.headingsx[0]
                self.headingy_sum -= self.headingsy[0]
                del self.headingsx[0]
                del self.headingsy[0]
            self.heading = math.degrees(math.atan2(self.headingx_sum, self.headingy_sum))
            if self.heading < 0:
                self.heading += 360
        if roll is not None and roll >= -90 and roll <= 90:
            self.rolls.append(roll)
            self.roll_sum += roll
            if len(self.rolls) > ROLL_FILTER_WINDOW_SIZE:
                self.roll_sum -= self.rolls[0]
                del self.rolls[0]
            self.roll = roll - self.roll_sum / len(self.rolls)
        return self.heading, self.roll
