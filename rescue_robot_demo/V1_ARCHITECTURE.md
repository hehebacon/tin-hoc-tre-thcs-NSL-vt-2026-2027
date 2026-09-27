# Rescue Robot V1 Architecture

    WEB COMMAND CENTER
             |
        REST API :8787
             |
      +------+------+
      |             |
  Mission       Safety
      |             |
      +-- Robot Core+
             |
       Decision Engine
     /       |       \
 PATROL   RESCUE   AUTONOMOUS
             |
        Sensor Fusion
    /       |       |       \
  RGB    THERMAL   ENV      IMU
             |
      Hardware Adapter
             |
        ESP32 / Servos

## V1 status

- Offline simulation: complete
- A* navigation: complete
- Four operating modes: complete
- Mission lifecycle: complete
- Emergency stop / resume / return-home: complete
- Camera + thermal simulation: complete
- Environment telemetry: complete
- Battery / signal / IMU / GPS simulation: complete
- Web command center: complete
- ESP32 transport boundary: ready
- Real sensor drivers: hardware phase
- Real servo/PCA9685 output: hardware phase
