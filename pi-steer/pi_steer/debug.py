import time

def now():
    localtime = time.localtime()
    return '{}:{}:{}'.format(localtime.tm_hour, localtime.tm_min, localtime.tm_sec)

print('Start debugger')

def write(text: str) -> None:
    print('{} {}\n'.format(now(), text))
