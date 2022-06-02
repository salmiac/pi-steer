import numpy
import matplotlib.pyplot
import sys
import csv
import math
import time

def euler(qx, qy, qz, qw):
    if abs(qw) > 1 or abs(qx) > 1 or abs(qy) > 1 or abs(qz) > 1:
        return (None, None, None)
    norm = math.sqrt(qw*qw + qx*qx + qy*qy + qz*qz)
    if norm == 0:
        return (None, None, None)
 
    qx /= norm
    qy /= norm
    qz /= norm
    qw /= norm

    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll = math.degrees(math.atan2(sinr_cosp, cosr_cosp))

    sinp = 2 * (qw * qy - qz * qx)
    try:
        pitch = math.asin(sinp)
    except ValueError:
        return (None, None, None)
    pitch = math.degrees(pitch)

    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    heading = -math.degrees(math.atan2(siny_cosp, cosy_cosp))

    return (heading, roll, pitch)


try:
    filename = sys.argv[1]
    eulerfile = sys.argv[2]
except Exception as err:
    print(err)
    sys.exit(0)


t_set = []
qx_set = []
qy_set = []
qz_set = []
qw_set = []
t_euler = []
headings = []
pitches = []
rolls = []
e_t = []
e_headings = []
e_pitches = []
e_rolls = []
d_t = []
d_headings = []
d_pitches = []
d_rolls = []


try:
    with open(filename) as file:
        reader = csv.reader(file)
        for row in reader:
            # print(row)
            # sys.exit(0)
            t = float(row[0])
            qx = float(row[1])
            qy = float(row[2])
            qz = float(row[3])
            qw = float(row[4])
            t_set.append(t)
            qx_set.append(qx)
            qy_set.append(qy)
            qz_set.append(qz)
            qw_set.append(qw)
            (heading, roll, pitch) = euler(qx, qy, qz, qw)
            if heading is not None:
                t_euler.append(t)
                headings.append(heading)
                pitches.append(pitch)
                rolls.append(roll)
    with open(eulerfile) as file:
        reader = csv.reader(file)
        last_t = None
        last_heading = None
        last_pitch = None
        last_roll = None
        for row in reader:
            # print(row)
            # sys.exit(0)
            t = float(row[0])
            heading = float(row[1]) 
            pitch = float(row[2])
            roll = float(row[3])
            e_t.append(t)
            e_headings.append(heading)
            e_pitches.append(pitch)
            e_rolls.append(roll)
            if last_heading is not None:
                d_t.append(t)
                d_headings.append((heading-last_heading+180)%360-180)
                d_pitches.append(pitch-last_pitch)
                d_rolls.append(roll-last_roll)
            last_t = t
            last_heading = heading
            last_pitch = pitch
            last_roll = roll
except Exception as err:
    print(err)
    sys.exit(0)



# Fixing random state for reproducibility
numpy.random.seed(19680801)

dt = 0.01
t = numpy.arange(0, 30, dt)
nse1 = numpy.random.randn(len(t))                 # white noise 1
nse2 = numpy.random.randn(len(t))                 # white noise 2

# Two signals with a coherent part at 10Hz and a random part
s1 = numpy.sin(2 * numpy.pi * 10 * t) + nse1
s2 = numpy.sin(2 * numpy.pi * 10 * t) + nse2

fig, axs = matplotlib.pyplot.subplots(4, 1)
print(len(t_set), len(qx_set), len(qy_set), len(qz_set), len(qw_set))
axs[0].plot(t_set, qx_set, ',-', label='qx', linewidth=1)
axs[0].plot(t_set, qy_set, ',-', label='qy', linewidth=1)
axs[0].plot(t_set, qz_set, ',-', label='qz', linewidth=1)
axs[0].plot(t_set, qw_set, ',-', label='qw', linewidth=1)
#axs[1].set_ylabel('Euler angles')
# axs[0].set_xlim(0, 2)
axs[0].set_xlabel('time')
# axs[0].set_ylabel('s1 and s2')
# axs[0].grid(True)
axs[0].set_title('Quaternions')
axs[0].legend()

axs[1].plot(t_euler, headings, '.-', markersize=2, label='heading', linewidth=1)
axs[1].plot(t_euler, pitches,'.-', markersize=2, label='pitch', linewidth=1)
axs[1].plot(t_euler, rolls, '.-', markersize=2, label='roll', linewidth=1)
axs[1].set_xlabel('time')
axs[1].set_title('Euler angles')
axs[1].legend()

axs[2].plot(e_t, e_headings, '.-', markersize=2, label='heading', linewidth=1)
axs[2].plot(e_t, e_pitches,'.-', markersize=2, label='pitch', linewidth=1)
axs[2].plot(e_t, e_rolls, '.-', markersize=2, label='roll', linewidth=1)
axs[2].set_xlabel('time')
axs[2].set_title('Filtered Euler angles')
axs[2].legend()

axs[3].plot(d_t, d_headings, '.-', markersize=2, label='heading', linewidth=1)
axs[3].plot(d_t, d_pitches,'.-', markersize=2, label='pitch', linewidth=1)
axs[3].plot(d_t, d_rolls, '.-', markersize=2, label='roll', linewidth=1)
axs[3].set_xlabel('time')
axs[3].set_title('Filtered Euler delta')
axs[3].legend()

fig.tight_layout()
matplotlib.pyplot.show()
