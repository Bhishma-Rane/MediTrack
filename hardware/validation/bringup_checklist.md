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
- [ ] In ultrasonic mode, confirm the ECHO divider is fitted and the sense node
      is not connected directly to GPIO18.
- [ ] In microswitch mode, confirm U3 is unplugged and the switch is wired NO
      to the sense input and COM to ground.

## Unpowered electrical checks

- [ ] Measure resistance from 5V_PROTECTED to GND; investigate a near-short.
- [ ] Verify continuity from every connector ground to the common ground.
- [ ] Verify the 10 kΩ / 20 kΩ divider values individually.
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
- [ ] Measure the ultrasonic ECHO divider node while the sensor is active; it
      must never exceed the ESP32's GPIO maximum.
- [ ] Exercise each button and verify the idle high / pressed low levels.
- [ ] Confirm OLED remains stable while the buzzer switches.

## Mechanical validation

- [ ] Fit the removable insert and verify it cannot touch exposed electronics.
- [ ] Verify the sensor bracket fixes angle and distance repeatably.
- [ ] Verify lid travel does not pinch the harness.
- [ ] Verify buttons are recessed enough to resist accidental presses.
- [ ] Verify the OLED window and buzzer vent are protected from spills.
- [ ] Record calibrated closed/open distances; do not ship the default values
      without this record.
