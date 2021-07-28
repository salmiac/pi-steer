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
        (heading, roll, pitch) = bno.read()
        # print('Imu read took: ', time.time()-tic, 's.')
        time.sleep(0.1)

threading.Thread(target=reader).start()
