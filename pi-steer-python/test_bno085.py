from cmath import pi
import time
import pi_steer.bno08x
import pi_steer.debug

bno = pi_steer.bno08x.BNO08X(False)
bno.reader_thread.start()
while True:
    print(pi_steer.debug.now(), bno.get_orientation(), '\r', end='')
    time.sleep(0.02)
