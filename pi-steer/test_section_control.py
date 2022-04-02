import pi_steer.section_control
import time

sc = pi_steer.section_control.SectionControl()

sc.update(0b0000_0000_0000_0001)
sc.update(0b0000_0000_0000_0000)
print('start time', time.time())
time.sleep(1)
for n in range(10):
    sc.update(0b0000_0000_0000_0001)
    time.sleep(1)

print('end time', time.time())
