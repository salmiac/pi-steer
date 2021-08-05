import time
import pi_steer.bno085
import threading

heading = 0
roll = 0
pitch = 0

def reader():
    bno = pi_steer.bno085.BNO085()
    global heading
    global roll
    global pitch

    while True:
        tic = time.time()
        try:
            (heading, roll, pitch) = bno.read()
        except Exception as err:
            # pass
            print('IMU read failed', err)
        # print('Imu read took: ', time.time()-tic, 's.')
        time.sleep(0.01)

threading.Thread(target=reader).start()
