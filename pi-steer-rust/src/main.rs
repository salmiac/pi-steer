use clap::{Arg, Command};
use std::thread;
use std::time::Duration;
use std::sync::{Arc, Mutex};

pub mod debug;
pub mod hw;
pub mod config;
pub mod communication;

use crate::hw::{motor::MotorControl, imu::IMU, was::WAS, gps::GPS, pwm::PwmControl};
use crate::config::settings::Settings;
use crate::communication::agio::{Reader, Writer};

fn main() {
    let matches = Command::new("Pi-steer")
        .version("1.0")
        .author("Jaakko Yli-Luukko")
        .about("AgOpenGPS controller for Raspberry Pi")
        .arg(Arg::new("config")
                .short('c')
                .long("config")
                .value_name("FILE")
                .help("Sets a custom config file")
        )
        .arg(
            Arg::new("debug")
                .short('d')
                .long("debug")
                .help("Activate debug mode")
                
        )
        .get_matches();

    debug::write("Moe");

    let debug = matches.contains_id("debug");

    if debug {
        println!("Debug on");
    }

    debug::write("Start Settings");
    let settings_arc = Arc::new(Mutex::new(Settings::new(debug)));
    let mut imu: Option<IMU> = None;
    let settings = settings_arc.lock().unwrap();
    let is_imu = settings.bno085;
    let is_was = settings.was;
    let gps_port = settings.gps.clone();
    drop(settings);
    let _gps: GPS;
    if is_imu {
        debug::write("Start IMU");
        imu = Some(IMU::new(false).unwrap());
    }
    if ! gps_port.is_empty() {
        _gps = GPS::new(debug, gps_port);
    }
    let mut was: Option<WAS> = None;
    if is_was {
        debug::write("Start WAS");
        was = Some(WAS::new(Arc::clone(&settings_arc)).unwrap());
    }
    debug::write("Start Motor control");
    let motor_control = Arc::new(Mutex::new(MotorControl::new(Arc::clone(&settings_arc), debug)));
    debug::write("Start AgIO");
    let reader = Reader::new(Arc::clone(&settings_arc), Arc::clone(&motor_control), false);
    let rc = Arc::clone(&reader.sc.rc);
    reader.start();
    
    let mut heading: f32 = 0.0;
    let mut roll: f32 = 0.0;
    
    let writer = Writer::new(is_imu, debug);

    let mut pwm = PwmControl::new(16);
    debug::write("Start loop");

    loop {
        // Your processing logic here
        // Example:
        if let Some(imu) = &imu {
            (heading, roll, _) = imu.read();
        }
        
        let mut wheel_angle: f32 = 0.0;
        match was {
            Some(ref mut w) => wheel_angle = w.read(),
            None => (),
        }
        let mut motor = motor_control.lock().unwrap();
        let (direction, pwm_value) = motor.update_motor(wheel_angle);
        let mut switch_state: u8 = if motor.switch.is_low() { 0b1111_1101 } else { 0b1111_1111 };
        drop(motor);
        pwm.set(direction, pwm_value);
        let rc_lock = rc.lock().unwrap();
        let work_switch = rc_lock.work_switch.is_low();
        drop(rc_lock);
        if work_switch {
            switch_state &= 0b1111_1110;
        }
        writer.from_autosteer(wheel_angle, heading, roll, switch_state, pwm_value);

        thread::sleep(Duration::from_millis(10));
    }
}
