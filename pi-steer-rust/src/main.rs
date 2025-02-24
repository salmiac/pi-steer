use clap::{Arg, Command};
use std::thread;
use std::time::Duration;
use std::sync::{Arc, Mutex};

pub mod debug;
pub mod hw;
pub mod config;
pub mod communication;

use crate::hw::{motor::MotorControl, imu::IMU, was::WAS, gps::GPS, pressure_control::PressureControl, section_control::SectionControl};
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
    let settings = settings_arc.lock().unwrap();
    let is_steer_control = settings.steer_control;
    let is_imu = settings.bno085;

    // Init WAS
    let mut was: Option<WAS> = None;
    if settings.was {
        debug::write("Start WAS");
        was = Some(WAS::new(Arc::clone(&settings_arc)).unwrap());
    }
    
    // Init IMU
    let mut imu: Option<IMU> = None;
    if settings.bno085 {
        debug::write("Start IMU");
        imu = Some(IMU::new(false).unwrap());
    }

    // Init GPS
    let _gps: GPS;
    if ! settings.gps.is_empty() {
        _gps = GPS::new(debug, settings.gps.clone());
    }

    // Init sprayer pressure controller
    let mut pressure_control: Option<PressureControl> = None;
    if settings.sprayer_pressure_control {
        pressure_control = Some(PressureControl::new(
            settings.sprayer_pressure_control, 
            settings.pressure_control_up_gpio, 
            settings.pressure_control_down_gpio, 
            debug
        ));
    }
    
    // Init section controller
    let mut section_control: Option<SectionControl> = None;
    if settings.section_control_enable {
        section_control = Some(SectionControl::new(
            settings.relay_mode, 
            settings.impulse_seconds, 
            settings.impulse_gpio.clone(), 
            settings.relay_gpio.clone(), 
            settings.input_gpio.clone(), 
            settings.work_switch_gpio
        ).unwrap());
    }
    drop(settings);

    // Init Motor controller
    debug::write("Start Motor control");
    let mut motor_control: Option<MotorControl> = None;
    if is_steer_control {
        motor_control = Some(MotorControl::new(Arc::clone(&settings_arc), debug));

    }

    // Init AgIO communication
    debug::write("Start AgIO");
    let reader = Reader::new(Arc::clone(&settings_arc), false);
    reader.start();
    
    let mut heading: f32 = 0.0;
    let mut roll: f32 = 0.0;
    
    let writer = Writer::new(is_imu, debug);

    debug::write("Start loop");

    loop {
        if let Some(imu) = &imu {
            (heading, roll, _) = imu.read();
        }
        
        let mut wheel_angle: f32 = 0.0;
        match was {
            Some(ref mut w) => wheel_angle = w.read(),
            None => (),
        }
        let mut switch_state: u8 = 0b1111_1111;
        let pwm_value = 0.0;
        match motor_control {
            Some(ref mut motor_control) => {
                motor_control.set_control(reader.get_steer_angle(), reader.get_status());
                let (direction, pwm_value) = motor_control.update_motor(wheel_angle);
                if motor_control.switch.is_low() { 
                    switch_state = 0b1111_1101 
                };
                motor_control.pwm.set(direction, pwm_value);
            },
            None => ()
        }
        match pressure_control {
            Some(ref mut pressure_control) => {
                pressure_control.set_speed(reader.get_speed());
                pressure_control.update_control();
            },
            None => ()
        }
        
        let mut work_switch = false;
        match section_control {
            Some(ref mut sc) => {
                let rc_lock = sc.rc.lock().unwrap();
                work_switch = rc_lock.work_switch.is_low();
            },
            None => ()
        }

        if work_switch {
            switch_state &= 0b1111_1110;
        }
        writer.from_autosteer(wheel_angle, heading, roll, switch_state, pwm_value);

        thread::sleep(Duration::from_millis(10));
    }
}
