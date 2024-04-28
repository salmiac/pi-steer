
curl https://sh.rustup.rs -sSf | sh

sudo apt-get install libudev-dev

sudo usermod -a -G dialout $USER

# build
cargo build

# Run unit tests
cargo test

cargo test -- --nocapture

# Test single unit test
cargo test gps -- --nocapture

# Build release version
cargo build --release

Executable is target/release/pi-steer-rust