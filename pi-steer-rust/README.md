## prepare

```bash
curl https://sh.rustup.rs -sSf | sh
sudo apt-get install libudev-dev
sudo usermod -a -G dialout $USER
```

## build
```bash
cargo build
```

## Run unit tests
```bash
cargo test
```

```bash
cargo test -- --nocapture
```

## Test single unit test
```bash
cargo test gps -- --nocapture
```

## Build release version
```bash
cargo build --release
```

Executable is `target/release/pi-steer-rust` copy it to user root directory.

Set program to start at boot
```bash
sudo crontab -e
```
add line
```bash
@reboot pi-steer-rust &
```
