import time
import pi_steer.bno085
import threading

MAXIMUM_ROLL = 30 # degrees

heading = 0
roll = 0
pitch = 0

def reader(ic2):
    bno = pi_steer.bno085.BNO085(i2c)
    global heading
    global roll
    global pitch

    while True:
        tic = time.time()
        try:
            (_heading, _roll, _pitch) = bno.read()
            heading = _heading
            if _roll > MAXIMUM_ROLL:
                _roll = MAXIMUM_ROLL
            if _roll < -MAXIMUM_ROLL:
                _roll = -MAXIMUM_ROLL
            roll = _roll
            pitch = _pitch

        except Exception as err:
            # pass
            print('IMU read failed', err)
        # print('Imu read took: ', time.time()-tic, 's.')
        time.sleep(0.01)

def start(i2c):
    threading.Thread(target=reader, args=(i2c,)).start()
