import math
import pi_steer.debug as db

def quaternion_to_euler(qw, qx, qy, qz, debug=False):
    # Value sanity check
    if abs(qw) > 1 or abs(qx) > 1 or abs(qy) > 1 or abs(qz) > 1:
        db.write('Value error: {} {} {} {}'.format(qx, qy, qz, qw) )
        return (None, None, None)
    # Norm should always be 1, or very close to 1
    norm = math.sqrt(qw*qw + qx*qx + qy*qy + qz*qz)
    norm_error = abs(1 - norm)
    if norm_error > 0.01:
        db.write('Quaternion Norm error {}'.format(norm))
        return (None, None, None)
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll = math.degrees(math.atan2(sinr_cosp, cosr_cosp))

    sinp = 2 * (qw * qy - qz * qx)
    try:
        pitch = math.asin(sinp)
    except ValueError:
        if debug:
            db.write('Value error: {} {} {} {}'.format(qx, qy, qz, qw) )
        return (None, None, None)
    pitch = math.degrees(pitch)

    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    heading = -math.degrees(math.atan2(siny_cosp, cosy_cosp))
    return (heading, roll, pitch)
