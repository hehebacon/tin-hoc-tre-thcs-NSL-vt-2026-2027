"""Hardware boundary for future ESP32/sensor integration.

The demo can run without hardware. Real adapters should implement the same
logical methods and feed data into the robot core.
"""


class HardwareAdapter:
    def connect(self):
        raise NotImplementedError

    def read_telemetry(self):
        raise NotImplementedError

    def send_motion(self, command):
        raise NotImplementedError


class SimulatedHardware(HardwareAdapter):
    def __init__(self, sensors):
        self.sensors = sensors

    def connect(self):
        return True

    def read_telemetry(self):
        return self.sensors.snapshot()

    def send_motion(self, command):
        return {"accepted": True, "command": command}
