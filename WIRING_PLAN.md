# Robot V2 Wiring Plan

This is the planned wiring for an ESP32 DevKit-style controller. Pin labels vary by board, so verify the exact board pinout before connecting power.

## Power architecture

- Servos: separate regulated servo supply sized for the actual servo model.
- ESP32: regulated 5 V USB/VIN input as specified by the board.
- PCA9685 logic: 3.3 V-compatible I2C logic.
- All signal grounds must share a common reference.
- Do not power a bank of 12 servos from the ESP32 3.3 V or USB rail.

## I2C bus

| Device | ESP32 |
|---|---|
| PCA9685 SDA | GPIO 21 |
| PCA9685 SCL | GPIO 22 |
| IMU SDA | GPIO 21 |
| IMU SCL | GPIO 22 |
| Environmental SDA | GPIO 21 |
| Environmental SCL | GPIO 22 |

I2C devices share SDA/SCL and must have non-conflicting addresses.

## PCA9685 servo map

| Leg | Coxa | Femur | Tibia |
|---|---:|---:|---:|
| FL | 0 | 1 | 2 |
| FR | 3 | 4 | 5 |
| RL | 6 | 7 | 8 |
| RR | 9 | 10 | 11 |

Servo channel numbering is logical. The physical servo orientation must be calibrated before gait testing.

## Sensors

Recommended first hardware layer:

- IMU: MPU6050/compatible I2C IMU
- Environment: BME280/compatible I2C sensor
- Thermal: MLX90640/compatible thermal array on a companion path
- RGB camera: companion camera/ESP32-CAM or SBC camera

The repository keeps these behind interfaces so sensor libraries can be swapped without rewriting mission logic.

## Network

For the first hardware test:

ESP32 USB serial -> PC Robot OS

Only after serial telemetry and safety behavior are verified should Wi-Fi/network control be enabled.

## Mandatory safety sequence

1. Keep PCA9685 output disabled in firmware.
2. Connect one servo only.
3. Verify common ground.
4. Verify servo voltage separately.
5. Test center command with the mechanism unloaded.
6. Calibrate that channel.
7. Repeat one channel at a time.
8. Add the remaining servos.
9. Test one leg.
10. Test all four legs without walking.
11. Test gait with the robot physically secured/raised.
12. Only then perform slow ground tests.

A physical power cutoff must remain accessible. Software E-STOP is not the only safety mechanism.
