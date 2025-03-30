use clap::{Arg, Command};
use std::thread;
use std::time::{Duration, Instant};
use std::sync::{Arc, Mutex};

pub mod debug;
pub mod hw;
pub mod config;
pub mod communication;

use crate::hw::{
    motor::MotorControl, 
    imu::IMU, 
    was::WAS, 
    gps::GPS, 
    ads1115::ADS1115,
    pressure_control::PressureControl, 
    pressure_sensor::PressureSensor, 
    section_control::SectionControl
};
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

    // Init ADC
    let mut adc: Option<ADS1115> = None;
    if settings.was || settings.sprayer_pressure_control {
        debug::write("Start ADC");
        adc = Some(ADS1115::new().unwrap());
    }

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
    let mut pressure_sensor = PressureSensor::new(settings.sprayer_pressure_control, settings.sprayer_pressure_multiplier, settings.sprayer_pressure_add).expect("Is ADC present?");
    if settings.sprayer_pressure_control {
        pressure_control = Some(PressureControl::new(
            settings.sprayer_pressure_control, 
            settings.pressure_control_up_gpio, 
            settings.pressure_control_down_gpio,
            settings.sprayer_boom_locked_gpio
        ));
    }
    
    // Init section controller
    let mut section_control: Option<SectionControl> = None;
    if settings.section_control_enable {
        section_control = Some(SectionControl::new(
            settings.relay_mode, 
            settings.impulse_seconds, 
            settings.relay_gpio.clone(), 
            settings.input_gpio.clone(), 
            settings.work_switch_gpio,
            settings.manual_mode_gpio
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
    let pgn_data = Reader::new(Arc::clone(&settings_arc), false);
    
    let mut heading: f32 = 0.0;
    let mut roll: f32 = 0.0;
    
    let writer = Writer::new(is_imu, debug);
    let mut timer = Instant::now();
    let send_period = Duration::from_millis(50);

    debug::write("Start loop");
    loop {
        let mut send_autosteer_state = false;

        if let Some(imu) = &imu {
            (heading, roll, _) = imu.read();
            send_autosteer_state = true;
        }
        
        let mut wheel_angle: f32 = 0.0;
        match was {
            Some(ref mut w) => wheel_angle = w.angle(adc.as_mut().unwrap().read(0).unwrap()),
            None => (),
        }
        let mut switch_state: u8 = 0b1111_1111;
        let mut pwm_value = 0.0;

        match motor_control {
            Some(ref mut motor_control) => {
                motor_control.set_control(*pgn_data.steer_angle.read().unwrap(), *pgn_data.status.read().unwrap());
                let (direction, _pwm_value) = motor_control.update_motor(wheel_angle);
                pwm_value = _pwm_value;
                if motor_control.switch.is_low() { 
                    switch_state = 0b1111_1101 
                };
                motor_control.pwm.set(direction, pwm_value);
                send_autosteer_state = true;
            },
            None => ()
        }

        match pressure_control {
            Some(ref mut pressure_control) => {
                if *pgn_data.new_sprayer_data.read().unwrap() {
                    pressure_control.nozzle_size = *pgn_data.nozzle_size.read().unwrap();
                    pressure_control.nozzle_spacing = *pgn_data.nozzle_spacing.read().unwrap();
                    pressure_control.litres_per_ha = *pgn_data.litres_per_ha.read().unwrap();
                    pressure_control.min_pressure = *pgn_data.sprayer_min_pressure.read().unwrap();
                    pressure_control.max_pressure = *pgn_data.sprayer_max_pressure.read().unwrap();
                    pressure_control.nominal_pressure = *pgn_data.sprayer_nominal_pressure.read().unwrap();
                    pressure_control.active = *pgn_data.sprayer_activated.read().unwrap();
                    pressure_control.constant_pressure = *pgn_data.sprayer_constant_pressure.read().unwrap();

                    let mut new_sprayer_data = (*pgn_data).new_sprayer_data.write().unwrap();
                    *new_sprayer_data = false;
                }
                pressure_control.set_speed(*pgn_data.speed.read().unwrap());

                pressure_control.current_pressure = pressure_sensor.pressure(adc.as_mut().unwrap().read(1).unwrap());
                pressure_control.update_control();
            },
            None => ()
        }
        
        let mut work_switch = false;

        match section_control {
            Some(ref mut sc) => {
                if *pgn_data.new_section_data.read().unwrap() {
                    sc.update(*pgn_data.sections.read().unwrap());
                    let mut new_section_data = (*pgn_data).new_section_data.write().unwrap();
                    *new_section_data = false;
                }
                let rc_lock = sc.rc.lock().unwrap();
                work_switch = rc_lock.work_switch_gpio.is_low();
                send_autosteer_state = true;
            },
            None => ()
        }

        // Send frequency is 20 Hz        
        if send_autosteer_state && timer.elapsed() >= send_period {
            if work_switch {
                switch_state &= 0b1111_1110;
            }
            writer.from_autosteer(wheel_angle, heading, roll, switch_state, pwm_value);
            match pressure_control {
                Some(ref mut pressure_control) => {
                    writer.sprayer_status(
                        pressure_control.target_pressure, 
                        pressure_control.current_pressure, 
                        pressure_control.boom_gpio.is_low(), 
                        pressure_control.speed
                    );
                },
                None => ()
            }
                timer = Instant::now();
        }

        thread::sleep(Duration::from_millis(1));
    }
}
