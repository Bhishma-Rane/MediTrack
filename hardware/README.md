# MediTrack hardware — Part 1

This directory is the buildable hardware definition for **Part 1: system
architecture and hardware pinout** in `../meditrack_master_prompt_specification.md`.
It defines the prototype product, its electrical interfaces, wiring, safety
constraints, and a parametric enclosure. It deliberately does **not** claim
that opening a compartment proves that medication was consumed.

## Product definition

MediTrack is a low-voltage, single-compartment medication-access verifier:

1. A scheduled reminder is displayed and sounded locally.
2. The user opens the medication compartment.
3. A sensor detects the open/closed transition.
4. The user closes the compartment; the controller can then record an access
   event for the backend.
5. If the compartment is not opened during the grace window, the controller
   records a missed event and may notify a caregiver when Parts 2–4 are added.

The prototype has two mutually exclusive sensing options:

- **Preferred for a physical prototype:** a normally-open lid microswitch.
- **Demonstration/non-contact option:** an HC-SR04 ultrasonic module.

Only one sensor mode is populated at a time. The pin map reserves GPIO18 for
the conditioned ultrasonic `ECHO` signal; a microswitch uses the same logical
compartment-state input through the alternate connector wiring described in
`wiring/point_to_point_wiring.md`.

## Included artifacts

| Path | Purpose |
| --- | --- |
| `bom/meditrack_bom.csv` | Components, ratings, and approved prototype parts |
| `wiring/pinout.csv` | Machine-readable ESP32 pin assignment |
| `wiring/point_to_point_wiring.md` | Connector and wire-by-wire assembly instructions |
| `schematics/meditrack_block_diagram.svg` | Renderable circuit/block diagram with power and signal paths |
| `schematics/meditrack_block_diagram.mmd` | Mermaid source for the diagram |
| `enclosure/meditrack_enclosure.scad` | Parametric OpenSCAD product enclosure |
| `validation/power_budget.md` | Power, voltage, and bring-up calculations |
| `validation/bringup_checklist.md` | Safe first-power and validation procedure |
| `validation/part1_validate.py` | Offline validation of pinout/BOM/diagram invariants |

## Electrical rules that must not be skipped

- **Never connect conventional HC-SR04 `ECHO` directly to an ESP32 GPIO.**
  The divider in the sensor-conditioning diagram reduces 5 V to about 3.3 V.
- Use a certified, isolated 5 V USB supply. No mains wiring belongs inside the
  enclosure.
- The buzzer is driven through a MOSFET; GPIO19 must not source buzzer current
  directly. A 100 kΩ gate pulldown keeps it off during reset.
- GPIO2 and GPIO15 are boot-strapping pins. The LED circuits must not force a
  boot-invalid level; verify the exact ESP32 board during bring-up.
- Sensor uncertainty, a disconnected sensor, and an out-of-range reading are
  **not** evidence that a dose was taken.
- The 5 cm closed / 8 cm open thresholds are starting values and require
  calibration after the final lid and sensor bracket are installed.

## Build sequence

1. Buy the exact parts in `bom/meditrack_bom.csv` or an approved alternate.
2. Assemble the electronics on a breadboard or carrier, with the ESP32
   unpowered while checking continuity.
3. Follow `validation/bringup_checklist.md` using a current-limited supply.
4. Validate the ultrasonic divider or microswitch mode independently.
5. Print `enclosure/meditrack_enclosure.scad`, install the removable insert,
   then repeat sensor calibration with the real lid geometry.
6. Only after the hardware checks pass should firmware and backend integration
   be connected.

## Prototype limitations

This is an engineering prototype design, not a medical device. It has not
been validated for clinical use, child resistance, water resistance,
sterilization, accessibility certification, medication dispensing, or proof of
ingestion. A production product needs electrical safety, EMC/ESD, software,
human-factors, risk-management, and regulatory work before deployment.
