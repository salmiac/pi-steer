import time
import pi_steer.imu
import pi_steer.debug

imu = pi_steer.imu.IMU(False)
while True:
    print(pi_steer.debug.now(), imu.read(), '\r', end='')
    time.sleep(0.02)
