# XZORT RESCUE QUADRUPED — AI ARCHITECTURE

## Offline AI
The ESP32 remains autonomous without Internet:
- deterministic competition state machine
- line/intersection decisions
- obstacle handling
- pickup/classify/place states
- home/end-game transitions
- fault and safety handling
- Vietnamese/English local intent parser

Gemini is never required for the competition mission.

## Online AI — Gemini
When Wi-Fi has Internet, Gemini provides:
- natural-language chat
- state explanation
- diagnostics
- telemetry interpretation
- planning/debug suggestions

Online responses are advisory and do not directly write servo positions.

## Perception
Sensors are normalized into WorldState:
- line state and intersection
- obstacle and distance
- target detection
- pickup/place state
- target color and confidence
- home/end-game state
- sensor health

ColorSensorInterface and LineSensorInterface are hardware-independent adapters. Real sensor drivers can replace them without changing DecisionEngine.

## Safety boundary
Online AI -> advice/intent -> validated RobotCore -> MotionSafety -> MotionController

Competition path:
Sensors -> Perception -> WorldState -> DecisionEngine -> RobotCore -> MotionController

If Internet fails, the competition path remains available.

## Wi-Fi
ESP32 uses AP + STA:
- AP: XZORT-RESCUE for local control
- STA: optional configured router/hotspot for Internet
- AP remains available when STA is unavailable

No Wi-Fi or Gemini secret is stored in the public source.

## Remaining real-world work
Software interfaces are in place, but competition readiness still requires real sensor drivers, a real pickup/place mechanism, field calibration, real servo integration, and repeated end-to-end testing.