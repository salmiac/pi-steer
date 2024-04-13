use crate::hw::bno08x::BNO08X;
// use log::{info, warn};
use std::error::Error;
use std::thread;
use std::time::Duration;

pub struct IMU {
    device: BNO08X,
    base_roll: f32,
}

impl IMU {
    pub fn new(debug: bool) -> Result<Self, Box<dyn Error>> {
        let device = BNO08X::new(debug);
        let mut imu = IMU { device, base_roll: 0.0 };
        imu.calibrate();
        Ok(imu)
    }

    fn calibrate(&mut self) {
        for _ in 0..20 {
            thread::sleep(Duration::from_secs(1));
            let (_, roll, _, active) = self.device.get_orientation();
            if !active { continue }
            // Calibration logic
            if -45.0 < roll && roll < 45.0 { break }
            if -135.0 < roll && roll < -45.0 {
                self.base_roll = -90.0;
                break;
            }
            if 45.0 < roll && roll < 135.0 {
                self.base_roll = 90.0;
                break;
            }
            if roll > 135.0 || roll < -135.0 {
                self.base_roll = 180.0;
                break;
            }
        }
    }

    pub fn read(&self) -> (f32, f32, f32) {
        // Read from the device and adjust based on base_roll
        let (heading, mut roll, pitch, _) = self.device.get_orientation();
        roll -= self.base_roll;
        (heading, roll, pitch)
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn imutest() {
        let imu = IMU::new(false);
        let (heading, roll, pitch) = imu.expect("REASON").read();
        println!("Heading: {}, Roll: {}, Pitch: {}", heading, roll, pitch);
    }
}

