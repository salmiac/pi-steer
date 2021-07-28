import automationhat

def analog1():
    return automationhat.analog.one.read()

def input1():
    return automationhat.input.one.read()

def output1(onoff):
    if onoff:
        automationhat.output.one.on()        
    else:
        automationhat.output.two.off()

def output3(onoff):
    if onoff:
        automationhat.output.three.on()        
    else:
        automationhat.output.three.off()