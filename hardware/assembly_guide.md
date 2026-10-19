# MediTrack assembly guide and sensor alternatives

This is the practical build sheet for the printed prototype. The enclosure
model is an exploded fit-check model, so print one draft before committing to
final dimensions. All measurements are in millimetres.

## Where every part goes

| Part | Location in the printed case | Why it is needed |
| --- | --- | --- |
| ESP32-WROOM-32E development board | Electronics bay, mounted flat on standoffs near the rear wall; USB connector faces the cable opening | Main controller: time, alarm state, buttons, sensor, Wi-Fi, and event payloads |
| SH1106 OLED | Behind the rectangular front window; display face flush with or slightly behind the front panel | Shows time, next dose, alarm, sensor state, and Wi-Fi status |
| Medication insert | Removable tray centered inside the base | Keeps medication separate from electronics and allows cleaning/replacement |
| Lid sensor | At the lid hinge/edge, where lid movement is repeatable | Detects open/closed access; choose exactly one sensor method |
| Active buzzer | Under the buzzer vent holes in the upper/rear area, facing outward | Local reminder and missed-dose alarm |
| Three tactile buttons | Behind the three recessed front holes, in a horizontal row | Confirm, mute/snooze, and snooze controls |
| Green LED | Behind the left status-light hole | System OK / access verified indication |
| Red LED | Behind the right status-light hole | Alarm, missed dose, or fault indication |
| MOSFET and resistors | Electronics bay, on the controller carrier/breadboard | Protects the ESP32 from buzzer current and limits LED/sensor voltages |
| Power entry / USB cable | Through the rear cable opening, with a strain relief | Supplies safe isolated 5 V power; keep mains outside the enclosure |
| Fuse, reverse-polarity protection, capacitors | Immediately after power entry on the controller carrier | Protects against wiring mistakes and supply transients |

### Printed-case orientation

The OpenSCAD preview places the base at the origin, the removable tray inside
the base, and the lid exploded above/behind it. In the assembled product:

```text
FRONT
┌──────────────────────────────────────────────┐
│ [ OLED window ]     [green] [red] [buttons]   │
│                                              │
│       removable medication insert            │
│                                              │
│ electronics bay: ESP32, power, MOSFET       │
│                         sensor at lid edge   │
├──────────────── rear wall ──────────────────┤
│ USB power / cable strain relief   buzzer vent│
└──────────────────────────────────────────────┘
BACK
```

Do not put the ESP32 or exposed PCB underneath the medication insert. Leave
clearance for the USB plug, button travel, OLED header, and sensor harness.
Use standoffs or a removable carrier rather than gluing the PCB directly to
the print.

## Exact wiring for the default build

The complete connector tables are in `wiring/point_to_point_wiring.md`. The
short version is:

| Device | Connect to ESP32 / rail |
| --- | --- |
| OLED SDA | GPIO21; VCC to 3.3 V; GND to GND |
| OLED SCL | GPIO22; VCC to 3.3 V; GND to GND |
| Lid microswitch, preferred | GPIO18 with pull-up; switch between GPIO18 and GND |
| HC-SR04 TRIG, if used | GPIO5 |
| HC-SR04 ECHO, if used | ECHO -> 10 kΩ -> sense node; sense node -> 20 kΩ -> GND; sense node -> 1 kΩ -> GPIO18 |
| Buzzer | Positive to its rated rail; negative to Q1 drain; Q1 source to GND; Q1 gate to GPIO19; 100 kΩ gate-to-GND |
| Confirm button | GPIO4 to GND when pressed; internal pull-up |
| Mute/snooze button | GPIO16 to GND when pressed; internal pull-up |
| Snooze button | GPIO17 to GND when pressed; internal pull-up |
| Green LED | GPIO2 -> 680 Ω -> LED anode; LED cathode to GND |
| Red LED | GPIO15 -> 680 Ω -> LED anode; LED cathode to GND |

All grounds are common. Route the buzzer return directly back to the power
entry, not through the OLED or sensor return. Test the voltages before the
ESP32 is connected.

## Alternatives to the HC-SR04

You do **not** need to use an HC-SR04. For a medication lid, a direct
open/closed sensor is normally more reliable and simpler than measuring
distance.

| Available sensor type | Recommendation | Wiring change | Mechanical placement |
| --- | --- | --- | --- |
| Normally-open lever microswitch | **Best prototype choice** | GPIO18 with pull-up; NO to GPIO18, COM to GND | Screw or glue the switch body to the base near the hinge; lever contacts the lid when closed |
| Hall-effect digital sensor + small magnet | Good contactless choice | 3.3 V, GND, digital output to GPIO18; use a pull-up if open-collector | Sensor fixed in base; magnet fixed on lid; align within the sensor's specified gap |
| Reed switch + magnet | Simple and low power | One side to GPIO18, other to GND; use pull-up | Keep the reed switch protected from impact; magnet on lid; validate bounce |
| VL53L0X / VL53L1X time-of-flight | Good non-contact replacement | 3.3 V/GND and shared I2C SDA21/SCL22; its usual 0x29 address does not conflict with SH1106 0x3C/0x3D | Aim at a flat lid target; calibrate open/closed distance |
| IR break-beam or reflective IR module | Usable if the beam/target is stable | Usually 3.3 V/GND/output to GPIO18; verify output voltage | Mount emitter and receiver/reflector so lid movement reliably changes the beam |
| LDR, analog light sensor, or generic proximity board | Not preferred | Requires an ADC pin and shielding/calibration | Ambient light and medication color can cause false states |
| Load cell / weight sensor | Future enhancement only | Needs HX711 and more firmware/mechanics | Measures container weight, not lid access; does not replace an access sensor |

### What I need from your sensor inventory

Send the exact part number, board name, or a clear photo of each sensor you
have. The important markings are the supply voltage and pin labels. I can then
select one, update the pinout/BOM, and give you the exact three- or four-wire
wiring without guessing.

## Sensor selection decision

For the first physical prototype, use this order:

1. Lever microswitch if you have one and the lid can physically press it.
2. Hall sensor plus magnet if you want no contact and have a stable mounting
   gap.
3. VL53L0X/VL53L1X if you want a digital distance sensor and can mount a flat
   target on the lid.
4. HC-SR04 only if it is the sensor you already have or you specifically want
   an ultrasonic demonstration.

Regardless of sensor choice, firmware must debounce and require three stable
readings over at least 300 ms. An unknown or noisy reading must not become
`DOSE_TAKEN`.

## Current completion estimate

The source specification has five parts. Based on the repository as it exists
now:

- **Part 1 — hardware architecture:** complete as a documented prototype;
  physical assembly and calibration remain.
- **Part 2 — ESP32 firmware:** not implemented yet.
- **Part 3 — backend/API:** implemented in the existing Python project.
- **Part 4 — dashboard/reporting:** implemented in the existing Python project.
- **Part 5 — validation/demo preparation:** partially started with hardware
  bring-up and power checklists; full failure-mode tests and demo script remain.

That is approximately **3 of 5 specification parts represented in the
repository**, but not 60% of a production-ready medical product. The remaining
work is concentrated in firmware, hardware/firmware integration, physical
calibration, end-to-end testing, and safety/regulatory review.
