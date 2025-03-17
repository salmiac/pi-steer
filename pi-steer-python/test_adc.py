import time
import pi_steer.ads1115

_ADS111X_ADDRESS0 = 0b01001000
_ADS111X_ADDRESS1 = 0b01001001


adc = pi_steer.ads1115.ADS1115(_ADS111X_ADDRESS0, True)
while True:
    print(adc.read())
    time.sleep(1)
