# Prompt for an AI PCB design engineer — MediTrack Rev B

Copy the prompt below into an AI tool that can design KiCad hardware. The AI
must treat this as an engineering design task, not as permission to guess
unknown part dimensions or claim medical certification.

---

## BEGIN PROMPT

You are a senior electronics engineer and KiCad PCB designer. Design a
reproducible, manufacturable **prototype controller PCB** for the MediTrack
three-cylinder medication-access/dispenser concept described below.

Your job is to produce a complete electrical design package, not just a block
diagram. Use KiCad 8 or a later stable KiCad version and state the exact
version. Keep every design decision explicit and identify anything that cannot
be finalized until a real component datasheet or measurement is supplied.

### 1. Product scope

MediTrack is a low-voltage prototype. It has three removable, sanitized
medicine cylinders at the rear of the product. Each cylinder has a separate
one-dose gate and an independent 5 V, 180-degree positional servo. Only the
scheduled cylinder's servo may move for a dose. The cylinders normally remain
fixed; the servos actuate the gates.

The mechanical gate must be designed to fail closed using geometry, gravity,
or a return spring. A servo must not be the only thing preventing pills from
falling. The PCB controls the servos but does not prove that medication was
swallowed. The design is a prototype and is not a medical device.

Use inert test objects during development. Do not claim universal one-pill
dispensing: the gate must be calibrated for a specified object shape and size.

### 2. Required board architecture

Design one low-voltage controller/power PCB with:

1. ESP32-WROOM-32E development-board interface, preferably a socket/header
   footprint so the ESP32 module can be replaced without replacing the PCB.
2. 5 V protected input from a certified external adapter.
3. Separate high-current 5 V servo branch for three servos.
4. 3.3 V logic rail for the ESP32, OLED, and sensors.
5. Three servo connectors with separate PWM signals.
6. SH1106 OLED connector.
7. Lid/compartment sensor connector.
8. Optional chute confirmation sensor connector.
9. Three buttons, two status LEDs, and an active buzzer output.
10. Test points and clear silkscreen labels.

Do not place mains voltage on the PCB. The external supply must be an isolated,
certified low-voltage adapter.

### 3. Pin assignment — preserve unless you document a change

| Function | ESP32 GPIO | Connector/net |
|---|---:|---|
| OLED SDA | GPIO21 | J1 SDA |
| OLED SCL | GPIO22 | J1 SCL |
| Lid/compartment sensor | GPIO18 | J2 SENSE |
| Buzzer MOSFET gate | GPIO19 | Q1 gate |
| Cylinder 1 servo PWM | GPIO23 | J6 signal |
| Cylinder 2 servo PWM | GPIO25 | J8 signal |
| Cylinder 3 servo PWM | GPIO26 | J9 signal |
| Optional chute sensor | GPIO27 | J7 SENSE |
| Confirm button | GPIO4 | J4 BTN_CONFIRM |
| Mute/snooze button | GPIO16 | J4 BTN_MUTE_SNOOZE |
| Snooze button | GPIO17 | J4 BTN_SNOOZE |
| Green LED | GPIO2 | LED1 |
| Red LED | GPIO15 | LED2 |

Use 50 Hz hardware PWM for the servos. The firmware will calibrate safe pulse
widths; do not assume 0 degrees and 180 degrees are safe endpoints. Confirm
GPIO16 and GPIO17 are available on the exact ESP32 board and check GPIO2 and
GPIO15 boot-strapping behavior. If a pin assignment is unsafe for the chosen
board, stop, explain the conflict, and propose a documented replacement.

### 4. Connector requirements

Use keyed, polarized connectors where practical. Every connector must have
pin-1 marking, mating-part information, signal direction, voltage, and wire
color guidance in the assembly documentation.

#### J1 — OLED, 4 pins

1. 3V3
2. SDA / GPIO21
3. SCL / GPIO22
4. GND

The OLED module pin order is not universal. Add a warning in the documentation
to verify the actual module silk screen before connection.

#### J2 — lid/compartment sensor, 3 pins

1. SENSE / GPIO18
2. 3V3 sensor supply, if required
3. GND

The default sensor is a normally-open microswitch: NO to SENSE and COM to GND,
with a pull-up. Hall and reed sensors are allowed alternatives after their
voltage and output type are verified.

#### J4 — buttons, 4 pins

1. GPIO4 confirm
2. GPIO16 mute/snooze
3. GPIO17 snooze
4. GND

Buttons are normally open and connect their GPIO to GND when pressed.

#### J6, J8, J9 — cylinder servos, 3 pins each

1. Servo signal: J6 GPIO23, J8 GPIO25, J9 GPIO26
2. Protected/fused SERVO_5V
3. GND

Do not power any servo from an ESP32 GPIO or the 3.3 V rail. Use adequate
connector current rating and heavier power/ground copper than the signal trace.

#### J7 — optional chute confirmation sensor, 3 pins

1. SENSE / GPIO27
2. 3V3, unless the selected sensor explicitly needs another safe voltage
3. GND

The sensor only confirms that an object passed the chute; it does not prove
medicine identity, dosage, or ingestion.

#### J3 — buzzer, 2 pins

1. BUZZER+
2. BUZZER− / Q1 drain

The ESP32 must drive a MOSFET, not the buzzer current directly.

### 5. Power tree and protection

Implement and document this power tree:

```text
5V_IN
  -> input fuse F1
  -> reverse-polarity protection D1 or ideal-diode circuit
  -> protected 5V_LOGIC
       -> ESP32 board 5V/VIN input, only if the exact board supports it
       -> buzzer supply as appropriate
       -> 3.3 V regulator/ESP32 board 3V3 output for logic peripherals
  -> servo fuse F2
  -> SERVO_5V branch
       -> J6 servo 1
       -> J8 servo 2
       -> J9 servo 3
```

Provide a separate SERVO_5V copper region/branch and route its return directly
to the power-entry ground/star point. Do not route servo current through the
OLED, buttons, or sensor return.

Add:

- 100 nF ceramic bypass capacitors at every IC/module power entry.
- At least 470 uF near the ESP32/buzzer logic entry.
- Initially 2200 uF near the three-servo power distribution; calculate or
  measure the final value after selecting the servos.
- Fuse ratings selected from actual servo stall/startup current, not guesses.
- Reverse-polarity protection with acceptable voltage drop and current rating.
- Clearly labeled 5V, SERVO_5V, 3V3, and GND test points.
- Optional TVS/ESD protection if external cables are long or user-accessible.

The existing planning estimate is approximately 3.6 A worst-case for three
small servos plus logic. Verify the exact servo datasheets and recommend a
certified 5 V supply with practical margin, likely 4–5 A. Explain whether the
chosen ESP32 board regulator can safely handle the logic load and Wi-Fi peaks.

### 6. Buzzer and indicator circuits

Use a logic-level N-channel MOSFET such as AO3400A or another verified part.
Include:

- GPIO19 to gate through an optional small series resistor.
- 100 kOhm gate-to-GND pulldown.
- Buzzer powered from its rated rail.
- Flyback diode if the selected buzzer is magnetic or inductive.
- Green LED and red LED with individually calculated current-limiting
  resistors, default around 680 Ohm but verify the actual LED current.

Check the boot implications of GPIO2 and GPIO15. Do not use a strong external
pull that creates an invalid ESP32 boot strap level.

### 7. PCB layout requirements

Produce a two-layer prototype PCB unless you can prove a four-layer board is
needed. The layout must include:

- A continuous ground plane where practical.
- Short, wide servo power and ground traces sized for the measured current.
- Star or controlled-return strategy separating servo/buzzer current from
  sensitive logic and I2C.
- Decoupling capacitors beside their loads.
- ESP32 antenna keepout: no copper, traces, or tall metal parts under/in front
  of the antenna area according to the exact module reference design.
- Mounting holes and dimensions coordinated with the printed enclosure.
- No exposed sharp PCB edges near the removable cylinders or user surfaces.
- Silkscreen designators for every connector, fuse, test point, polarity mark,
  and servo channel.
- Pin-1 and connector orientation markings visible after assembly.
- Clearance around the ESP32 USB connector and all cable exits.

Use conservative trace widths and clearances for the selected PCB fabricator.
State the chosen manufacturer rules and DRC settings. Do not silently assume
the board house's defaults.

### 8. Safety and fail-safe requirements

The PCB and design documentation must ensure:

- All three servo outputs initialize inactive and do not move during reset or
  boot until firmware explicitly commands a safe closed position.
- A power interruption cannot cause an automatic dispense on reboot.
- A disconnected lid sensor resolves to open/unknown, not successful dose.
- A jam or missing chute confirmation does not cause unlimited retry motion.
- Only the scheduled cylinder is enabled for a dispense operation.
- The PCB cannot claim that a medicine was swallowed.
- The servo branch cannot back-feed the logic rail.
- The board has no mains voltage.
- First power-up can be done with a current-limited bench supply.

### 9. Required design outputs

Create all of these outputs:

1. KiCad project file.
2. Complete schematic with ERC-clean results or documented exceptions.
3. PCB layout with DRC-clean results or documented exceptions.
4. Fabrication outputs: Gerbers, drill files, board outline, and stack-up.
5. Interactive BOM with manufacturer part numbers, footprints, substitutes,
   lifecycle status, and prototype cost estimate.
6. Pick-and-place/CPL file if assembly is planned.
7. PDF schematic and assembly drawing.
8. Connector pinout and cable/harness table.
9. Power-budget calculation using the exact chosen components.
10. Bring-up procedure with resistance, voltage, and current checks.
11. Test-point map and oscilloscope/multimeter checks.
12. A revision-controlled README with exact KiCad version, fab settings,
    build order, programming method, and known limitations.

### 10. Required verification procedure

Before connecting the ESP32:

1. Inspect polarity, orientation, solder bridges, and connector pin 1.
2. Measure resistance from 5V_IN, 5V_LOGIC, SERVO_5V, and 3V3 to GND.
3. Power the board without servos using a current-limited supply.
4. Verify protected 5 V and 3.3 V rails.
5. Verify the servo branch separately with a dummy load/current limit.
6. Connect one servo and measure startup and stall current briefly and safely.
7. Connect the remaining servos one at a time; never begin with pills.
8. Verify that GPIO23/25/26 signals are 50 Hz and have the intended safe pulse
   widths.
9. Confirm all servos remain mechanically closed during reset, boot, Wi-Fi
   reconnect, and power recovery.
10. Verify buttons, LEDs, OLED, lid sensor, buzzer, and chute sensor separately.
11. Test jam, empty cylinder, wrong-cylinder selection, lid-open, chute timeout,
    brownout, and reset conditions.

### 11. Unknowns you must not guess

The following are not final and must be requested or clearly marked as
assumptions:

- Exact ESP32 development-board manufacturer and pin/header dimensions.
- Exact servo model, stall current, connector polarity, body dimensions, and
  actual safe PWM pulse range.
- Exact cylinder dimensions and gate mechanism.
- Exact medicine/test-object dimensions and mass.
- Exact OLED module pin order and supply range.
- Exact chute sensor model and output voltage.
- PCB dimensions, mounting-hole locations, and enclosure constraints.
- Intended PCB manufacturer and assembly house.

If any of these unknowns changes schematic safety, power sizing, footprint,
or mechanical fit, stop and ask targeted questions before finalizing the PCB.
Do not fabricate datasheet values or use a generic footprint without labeling
it as provisional.

### 12. Final response format

Return your work in this order:

1. Design assumptions and questions blocking finalization.
2. Architecture summary.
3. Pin/connector table.
4. Complete power and protection design.
5. Schematic design decisions.
6. PCB placement and routing plan.
7. Exact output-file list.
8. ERC/DRC and electrical test results.
9. BOM and procurement warnings.
10. Remaining risks and the next physical prototype step.

Never report the PCB as production-ready or medically certified. Use the words
"prototype" and "requires physical validation" where appropriate.

## END PROMPT

---

## How to use this prompt

Before sending it to a PCB-design AI, fill in these values:

1. Exact ESP32 board model.
2. Exact servo model for all three channels.
3. Exact cylinder diameter and height.
4. Exact test-object/pill dimensions.
5. Exact lid sensor and chute sensor.
6. Printed-case mounting-hole coordinates.
7. Preferred PCB manufacturer.

There are two important values to verify before ordering a PCB:

- J2 is now specified as a three-pin lid-sensor connector. Verify that the
  selected microswitch, Hall, or reed sensor needs only SENSE/3V3/GND.
- The planning supply is now a certified 5 V, 5 A adapter, but the final
  rating and servo fuse must still be based on the exact three-servo stall
  current. Do not substitute a 2 A adapter without measurement.

The current project files contain the design context referenced by this prompt:

- `hardware/full_product_design.md`
- `hardware/wiring/pinout.csv`
- `hardware/wiring/point_to_point_wiring.md`
- `hardware/bom/meditrack_bom.csv`
- `hardware/validation/power_budget.md`
