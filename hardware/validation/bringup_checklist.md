# Part 1 bring-up checklist

Perform these checks with the ESP32 disconnected until the continuity and rail
checks pass. Use a current-limited bench supply for first power.

## Before power

- [ ] Confirm the exact ESP32 board exposes every assigned GPIO and does not
      reserve GPIO16/17 for PSRAM.
- [ ] Confirm OLED voltage and connector pin order from its datasheet/silk.
- [ ] Confirm B1 voltage/current and whether it is piezo or inductive.
- [ ] Inspect polarity of D1, C6, LEDs, Q1, and all keyed connectors.
- [ ] Confirm no 5 V net is shorted to any ESP32 GPIO.
- [ ] Confirm no ultrasonic sensor is installed; use a 3.3 V-safe microswitch,
      Hall sensor, or reed switch for the compartment state.
- [ ] Confirm the lid sensor is wired to GPIO18 and has no floating input when
      its harness is disconnected.
- [ ] Confirm the servo is a known 5 V part and is not powered from 3.3 V or an
      ESP32 GPIO.

## Unpowered electrical checks

- [ ] Measure resistance from 5V_PROTECTED to GND; investigate a near-short.
- [ ] Verify continuity from every connector ground to the common ground.
- [ ] Verify the selected lid sensor voltage and pull-up/pull-down wiring.
- [ ] Confirm Q1 source is GND, drain is B1 negative, and gate is GPIO19.
- [ ] Confirm LED1/LED2 each have a series resistor.
- [ ] Check that GPIO2/GPIO15 are not hard-pulled to an invalid boot level.

## First power, ESP32 disconnected

- [ ] Set supply to 5.0 V and a conservative current limit.
- [ ] Power the protected rail and measure 5V_PROTECTED.
- [ ] Measure 3V3 at the ESP32 board input/header; it must match the exact
      board's stated tolerance.
- [ ] Power off and discharge before reconnecting modules.

## First power, ESP32 connected

- [ ] Observe startup current and brownout behavior.
- [ ] Confirm buzzer is silent while GPIO19 is reset.
- [ ] Confirm LEDs do not prevent boot.
- [ ] Measure the servo branch voltage before connecting the servo signal.
- [ ] Verify the servo gate has a hard closed stop and cannot enter the pill
      path or electronics bay.
- [ ] Exercise each button and verify the idle high / pressed low levels.
- [ ] Confirm OLED remains stable while the buzzer switches.
- [ ] Move the servo through calibrated endpoints with no pills installed;
      verify it cannot bind, overtravel, or open the gate at boot.
- [ ] Test a chute jam and power interruption; the system must stop and require
      inspection rather than retrying indefinitely.

## Mechanical validation

- [ ] Fit the removable insert and verify it cannot touch exposed electronics.
- [ ] Verify the sensor bracket fixes angle and distance repeatably.
- [ ] Verify lid travel does not pinch the harness.
- [ ] Verify buttons are recessed enough to resist accidental presses.
- [ ] Verify the OLED window and buzzer vent are protected from spills.
- [ ] Record calibrated closed/open distances; do not ship the default values
      without this record.
