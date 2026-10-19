# MediTrack hardware — Part 1

This directory is the buildable hardware definition for **Part 1: system
architecture and hardware pinout** in `../meditrack_master_prompt_specification.md`.
It defines the prototype product, its electrical interfaces, wiring, safety
constraints, and a parametric enclosure. It deliberately does **not** claim
that opening a compartment proves that medication was consumed.

## Product definition

MediTrack is a low-voltage, single-dose-at-a-time medication dispenser and
access verifier:

1. A scheduled reminder is displayed and sounded locally.
2. After local confirmation, a servo opens a mechanically constrained,
   one-dose gate over a chute.
3. An optional chute sensor confirms that an object passed through; a lid sensor
   detects whether the user accessed the collection compartment.
4. The user opens and closes the collection compartment; the controller can
   record access and dispense events for the backend.
5. If dispensing is jammed, uncertain, or interrupted, the controller stops,
   alarms, and requires inspection rather than retrying indefinitely.

The prototype has two mutually exclusive sensing options:

- **Preferred compartment sensor:** a normally-open lid microswitch on GPIO18.
- **Contactless alternative:** a Hall sensor or reed switch with a lid magnet.
- **Optional dispense confirmation:** a 3.3 V-safe optical break-beam or chute
  flap sensor on GPIO27.

The product no longer uses an HC-SR04. GPIO18 is the 3.3 V-safe lid sensor
input. GPIO23, GPIO25, and GPIO26 control the three 5 V cylinder servos on a
dedicated fused power branch. GPIO27 is reserved for optional chute
confirmation.

## Included artifacts

| Path | Purpose |
| --- | --- |
| `bom/meditrack_bom.csv` | Components, ratings, and approved prototype parts |
| `wiring/pinout.csv` | Machine-readable ESP32 pin assignment |
| `wiring/point_to_point_wiring.md` | Connector and wire-by-wire assembly instructions |
| `wiring/esp32_firmware_wiring.md` | Part 2 firmware wiring quick reference and bring-up order |
| `assembly_guide.md` | Physical placement, printed-case assembly, sensor alternatives, and completion status |
| `full_product_design.md` | Complete dispensing mechanism, product layout, state flow, and limitations |
| `schematics/meditrack_block_diagram.svg` | Renderable circuit/block diagram with power and signal paths |
| `schematics/meditrack_block_diagram.mmd` | Mermaid source for the diagram |
| `enclosure/meditrack_enclosure.scad` | Parametric OpenSCAD product enclosure |
| `validation/power_budget.md` | Power, voltage, and bring-up calculations |
| `validation/bringup_checklist.md` | Safe first-power and validation procedure |
| `validation/part1_validate.py` | Offline validation of pinout/BOM/diagram invariants |

## Electrical rules that must not be skipped

- Use a certified, isolated 5 V USB supply. No mains wiring belongs inside the
  enclosure.
- The servo is powered from a dedicated, fused 5 V branch; never power it from
  an ESP32 GPIO or 3.3 V output. Add a bulk capacitor near the servo.
- The servo gate must have a positive closed stop and must be mechanically
  fail-closed. A servo position alone is not proof that a pill was dispensed.
- The buzzer is driven through a MOSFET; GPIO19 must not source buzzer current
  directly. A 100 kΩ gate pulldown keeps it off during reset.
- GPIO2 and GPIO15 are boot-strapping pins. The LED circuits must not force a
  boot-invalid level; verify the exact ESP32 board during bring-up.
- Sensor uncertainty, a disconnected sensor, a jam, or a missing chute
  confirmation are **not** evidence that a dose was taken.
- Dispense events should be separated into attempted and confirmed. Neither
  proves the medication was swallowed.

## Build sequence

1. Buy the exact parts in `bom/meditrack_bom.csv` or an approved alternate.
2. Assemble the electronics on a breadboard or carrier, with the ESP32
   unpowered while checking continuity.
3. Follow `validation/bringup_checklist.md` using a current-limited supply.
4. Validate the lid sensor and all three servo gates independently with inert test
   objects; do not begin with real medication.
5. Print `enclosure/meditrack_enclosure.scad`, install the removable insert,
   three cylinders, three gates, chute, servo brackets, and lid sensor.
6. Calibrate the gate for one known object shape and test jam/power-loss cases.
7. Only after the hardware checks pass should firmware and backend integration
   be connected.

## Prototype limitations

This is an engineering prototype design, not a medical device. It has not
been validated for clinical use, child resistance, water resistance,
sterilization, accessibility certification, medication dispensing, or proof of
ingestion. A production product needs electrical safety, EMC/ESD, software,
human-factors, risk-management, and regulatory work before deployment.
