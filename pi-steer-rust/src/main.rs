use clap::{App, Arg};
use std::thread;
use std::time::Duration;
use std::sync::{Arc, Mutex};
use rppal::gpio::{Gpio};

pub mod debug;
pub mod hw;
pub mod config;
pub mod communication;

use crate::hw::{motor::MotorControl, imu::IMU, was::WAS};
use crate::config::settings::Settings;
use crate::communication::agio::{Reader, Writer};

fn main() {
    debug::write("Moe");

    let matches = App::new("Pi Steer")
        .version("1.0")
        .arg(Arg::with_name("debug")
             .short("d")
             .long("debug")
             .help("Activates debug mode"))
        .get_matches();

    let debug = matches.is_present("debug");

    if debug {
        println!("Debug on");
    }

    // Setup GPIO pin for work switch
    let gpio = Gpio::new().expect("Failed to access GPIO");
    let work_switch = gpio.get(13).expect("Failed to access GPIO pin").into_input_pullup();

    // Initialize your components here (imu, settings, was, motor_control, agio)
    // Placeholder: actual initialization depends on your implementation
    
    debug::write("Start Settings");
    let settings_arc = Arc::new(Mutex::new(Settings::new(debug)));
    let mut imu: Option<IMU> = None;
    let settings = settings_arc.lock().unwrap();
    let is_imu = settings.bno085;
    if is_imu {
        debug::write("Start IMU");
        imu = Some(IMU::new(debug).unwrap());
    }
    drop(settings);
    debug::write("Start WAS");
    let mut was = WAS::new(Arc::clone(&settings_arc)).unwrap();
    debug::write("Start Motor control");
    let motor_control = Arc::new(Mutex::new(MotorControl::new(Arc::clone(&settings_arc))));
    debug::write("Start AgIO");
    let reader = Reader::new(Arc::clone(&settings_arc), Arc::clone(&motor_control), debug);
    reader.start();

    let mut heading: f32 = 0.0;
    let mut roll: f32 = 0.0;
    
    let writer = Writer::new(is_imu, debug);

    debug::write("Start loop");
    loop {
        // Your processing logic here
        // Example:
        if let Some(imu) = &imu {
            (heading, roll, _) = imu.read();
        }

        let wheel_angle = was.read();
        let mut motor = motor_control.lock().unwrap();
        motor.update_motor(wheel_angle);
        let mut switch_state: u8 = if motor.switch.is_high() { 0b1111_1101 } else { 0b1111_1111 };
        // Work switch

        if work_switch.is_low() {
            switch_state &= 0b1111_1110;
        }
        writer.from_autosteer(wheel_angle, heading, roll, switch_state, motor.pwm_value);

        thread::sleep(Duration::from_millis(10));
    }
}
