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
    
    def euler(self):
        return self.imu.euler