import pi_steer.automation_hat as hat

def angle():
    return (hat.analog1() - 2.5) / 2.0 * 60.0
