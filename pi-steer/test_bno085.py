import time
import pi_steer.bno085
import numpy

bno = pi_steer.bno085.BNO085()

headings = []
rolls = []
pitches = []

while True:
    tic = time.time()
    (heading, roll, pitch) = bno.read()
    headings.append(heading)
    rolls.append(roll)
    pitches.append(pitch)

    min_heading = numpy.amin(headings)
    max_heading = numpy.amax(headings)
    min_roll = numpy.amin(rolls)
    max_roll = numpy.amax(rolls)
    min_pitch = numpy.amin(pitches)
    max_pitch = numpy.amax(pitches)

    print('\rMin H {: = 7.2f} P {: = 7.2f} R {: = 7.2f} Max H {: = 7.2f} P {: = 7.2f} R {: = 7.2f}   '.format(min_heading, min_pitch, min_roll, max_heading, max_pitch, max_roll), end='')


    time.sleep(0.01)

