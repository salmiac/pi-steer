import time
import pi_steer.bno08x
import threading

MAXIMUM_ROLL = 30 # degrees

heading = 0
roll = 0
pitch = 0

def reader():
    bno = pi_steer.bno08x.BNO08X()
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

def start():
    threading.Thread(target=reader).start()
