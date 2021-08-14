import time
import numpy
import pi_steer.bno08x
import pi_steer.i2c

i2c = pi_steer.i2c.get_i2c()

bno = pi_steer.bno08x.BNO08X(i2c)

headings = []
rolls = []
pitches = []

n = 0

while True:
    tic = time.time()
    n += 1
    (heading, roll, pitch) = bno.read()
    heading = (heading + 180) % 360
    headings.append(heading)
    rolls.append(roll)
    pitches.append(pitch)

    # print('\r H {: = 7.2f} P {: = 7.2f} R {: = 7.2f}   '.format(heading, pitch, roll))
    # time.sleep(0.1)
    # continue

    min_heading = numpy.amin(headings)
    max_heading = numpy.amax(headings)
    min_roll = numpy.amin(rolls)
    max_roll = numpy.amax(rolls)
    min_pitch = numpy.amin(pitches)
    max_pitch = numpy.amax(pitches)

    print('\rMin H {: = 7.2f} P {: = 7.2f} R {: = 7.2f} Max H {: = 7.2f} P {: = 7.2f} R {: = 7.2f}  {} '.format(min_heading, min_pitch, min_roll, max_heading, max_pitch, max_roll, n), end='')


    time.sleep(0.01)

