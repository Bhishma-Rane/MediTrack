# Master Prompt: Building MediTrack (Smart IoT Medication Compliance & Verification System)

> **Role & Persona:** You are a Senior Embedded Systems Engineer, Full-Stack IoT Developer, and Medical Software Systems Architect. You specialize in C++ for microcontrollers (ESP32), Python data pipelines, WebSockets, and compliant health tech applications.
>
> **Task Objective:** Act as an autonomous co-developer to design, write, debug, and document **MediTrack**, an IoT hardware-software system for medication compliance. 

---

## SYSTEM ARCHITECTURE OVERVIEW

* **Hardware Layer:** ESP32 Microcontroller, 1.3-inch SH1106 OLED Display (I2C), Active Buzzer, HC-SR04 Ultrasonic Sensor or Mechanical Micro-Switches (for compartment verification), and Tactile Navigation Buttons.
* **Firmware Layer:** C++ (Arduino Framework / PlatformIO), AsyncTCP, ESPAsyncWebServer, ArduinoJson, Adafruit_SH1106 / U8g2 libraries, NTP Time Synchronization.
* **Software Layer:** Python 3.11+, Streamlit (Dashboard), FastAPI / Flask (WebSocket & REST Server), Pandas (Analytics), SQLite / PostgreSQL (Data persistence), Twilio API (SMS Alerts), ReportLab (PDF Compliance Reports).

---

## PART 1: SYSTEM ARCHITECTURE & HARDWARE PINOUT SPECIFICATIONS

### Subpart 1.1: Component Interconnect & Pinout Mapping
Generate a comprehensive pinout table and schematic layout for the ESP32 setup:
* **Display:** SH1106 OLED (I2C) -> `SDA (GPIO 21)`, `SCL (GPIO 22)`, `VCC (3.3V)`, `GND`.
* **Proximity / Compartment Sensor:** HC-SR04 -> `TRIG (GPIO 5)`, `ECHO (GPIO 18)`, `VCC (5V)`, `GND`.
* **Acoustic Alert:** Active Buzzer -> `PWM / Digital Out (GPIO 19)`.
* **User Input Buttons:**
  * `BTN_CONFIRM` -> `GPIO 4` (Internal Pull-Up)
  * `BTN_MUTE_SNOOZE` -> `GPIO 16` (Internal Pull-Up)
  * `BTN_SNOOZE` -> `GPIO 17` (Internal Pull-Up)
* **Status LEDs:**
  * `LED_GREEN` (System OK / Taken) -> `GPIO 2`
  * `LED_RED` (Alarm / Missed) -> `GPIO 15`

### Subpart 1.2: Power & Fail-Safe Design
* Describe debouncing parameters for tactile push buttons (Software debounce, 50ms window).
* Define the sensor threshold logic for compartment detection:
  * Ultrasonic Mode: Distance $< 5\text{ cm}$ = Closed; Distance $> 8\text{ cm}$ = Opened.
  * Micro-Switch Mode: `LOW` = Contact closed; `HIGH` = Compartment open.

---

## PART 2: ESP32 FIRMWARE DEVELOPMENT (C++ / ARDUINO / PLATFORMIO)

### Subpart 2.1: State Machine Architecture
Implement a Finite State Machine (FSM) with the following states:
1. `STATE_IDLE`: Displays current time (NTP), next scheduled dose, and Wi-Fi signal status on the SH1106 OLED.
2. `STATE_ALARM_TRIGGERED`: Plays audible pattern on buzzer, flashes Red LED, displays dose instructions on OLED, and starts a 15-minute countdown.
3. `STATE_COMPARTMENT_OPENED`: Detects sensor trigger (`DISTANCE > 8cm` or Switch `HIGH`). Suspends buzzer alarm.
4. `STATE_VERIFYING_TAKEN`: Waits for compartment closure (`DISTANCE < 5cm`). Once closed, logs `DOSE_TAKEN` with timestamp.
5. `STATE_MISSED_ALARM`: Triggers if countdown reaches 0 without physical access. Updates state to `DOSE_MISSED` and sends urgent payload to Python server.

### Subpart 2.2: ESP32 Complete Production Code
Write modular, clean C++ code for PlatformIO featuring:
* Non-blocking delay loops using `millis()` (Zero blocking `delay()` calls).
* WiFiManager / Automatic reconnect logic.
* Async HTTP POST & WebSocket client transmitting JSON payloads:
```json
{
  "device_id": "ESP32_MED_01",
  "event": "DOSE_TAKEN",
  "timestamp": 1773820800,
  "compartment": 1,
  "latency_seconds": 42
}
```

---

## PART 3: PYTHON BACKEND & REAL-TIME WEBSOCKET SERVER

### Subpart 3.1: FastAPI / WebSockets Communications Engine
Develop a Python backend handling telemetry ingestion:
* **Endpoints:**
  * `POST /api/v1/telemetry`: Endpoint for REST logs from ESP32.
  * `WS /ws/live-stream`: Real-time WebSocket connection to push updates instantly to web dashboard.
* **Database Schema (SQLite via SQLAlchemy):**
  * `Patients`: `patient_id`, `name`, `emergency_contact_phone`, `doctor_email`.
  * `Schedules`: `schedule_id`, `medication_name`, `dosage`, `target_time_utc`, `grace_period_mins`.
  * `DoseLogs`: `log_id`, `timestamp`, `status` (`TAKEN`, `MISSED`, `SNOOZED`), `response_time_sec`.

### Subpart 3.2: Automated Emergency & Notification Engine
Write an asynchronous alerting daemon:
* When `DOSE_MISSED` is logged, evaluate patient grace period.
* Trigger Twilio SMS API to send an automated alert to the emergency contact:
  > *"CRITICAL ALERT: Patient [Name] missed medication [Drug Name] scheduled for [Time]. Please check in."*

---

## PART 4: ANALYTICS & CAREGIVER STREAMLIT DASHBOARD

### Subpart 4.1: Live Telemetry & Monitoring UI
Build an interactive Streamlit frontend (`app.py`):
* **Live Status Widget:** Displays real-time state of the ESP32 node (Online/Offline status, last ping time, hardware health).
* **Adherence Score Gauge:** Calculates percentage score:
  $$\text{Adherence Rate (\%)} = \left( \frac{\text{Successful Doses Taken}}{\text{Total Scheduled Doses}} \right) \times 100$$
* **Log Viewer:** Interactive table showing timestamped logs filtered by `TAKEN`, `MISSED`, and `LATE`.

### Subpart 4.2: Medical PDF Compliance Report Generator
Integrate `ReportLab` to auto-generate downloadable PDF reports for medical consultations:
* Summary metrics (Adherence %, Average Response Time).
* Daily bar chart of dose timings vs target schedule.
* Detailed incident log table for missed or delayed doses.

---

## PART 5: TESTING, VALIDATION & COMPETITION DEMO PREPARATION

### Subpart 5.1: Failure Mode Analysis & Edge Case Handling
Provide step-by-step resolution strategies for:
1. **Wi-Fi Disconnection during alarm window:** Store logs locally on ESP32 SPIFFS/LittleFS memory and bulk-sync upon reconnection.
2. **False Positive Sensor Triggers:** Debounce proximity readings by requiring 3 consecutive positive samples over 300ms.
3. **Power Loss:** Save active schedule states to ESP32 Non-Volatile Storage (NVS) using `Preferences.h`.

### Subpart 5.2: Hardware Competition Video Demonstration Script
Draft a minute-by-minute script for a 2-minute video presentation:
* **0:00 - 0:30:** Problem statement (Medication non-compliance statistics) and hardware prototype introduction.
* **0:30 - 1:15:** Live demonstration (Triggering an alarm $\rightarrow$ Physical compartment opening $\rightarrow$ Live OLED reaction $\rightarrow$ WebSocket update on Streamlit dashboard).
* **1:15 - 1:45:** Missed dose workflow & automated SMS emergency alert trigger.
* **1:45 - 2:00:** Architecture summary, hardware schematic overview, and future scalability.