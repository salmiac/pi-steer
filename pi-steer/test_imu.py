import time
import pi_steer.imu

imu = pi_steer.imu.IMU(True)
while True:
    imu.read()
    time.sleep(0.3)
