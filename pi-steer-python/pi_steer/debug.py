import time

def now():
    localtime = time.localtime()
    return '{:02d}:{:02d}:{:02d}'.format(localtime.tm_hour, localtime.tm_min, localtime.tm_sec)

print('Start debugger')

def write(text: str) -> None:
    print('\n{} {}'.format(now(), text))
