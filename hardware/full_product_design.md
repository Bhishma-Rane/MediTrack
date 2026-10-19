# Full MediTrack prototype design

## Product architecture

The first dispensing prototype uses a **gravity-fed hopper, a one-dose gate,
and a collection cup**. The servo does not try to count pills by spinning
continuously. It moves a gate between two calibrated positions:

1. **Closed:** the gate blocks the hopper outlet.
2. **Dispense:** one pocket/opening aligns with the chute.
3. **Closed:** the gate returns to the hard stop.

The gate and pocket must be sized and tested for one specific inert test object
first. Round tablets, capsules, and irregular pills do not behave identically.
The prototype must not claim universal one-pill dispensing.

## Mechanical layout

Front view:

```text
┌──────────────────────────────────────────────────────────┐
│  OLED window        green LED  red LED  confirm/mute/snooze│
├──────────────────────────────────────────────────────────┤
│  HOPPER BAY                 SERVO BAY       CHUTE / CUP   │
│  ┌──────────────┐       ┌─────────┐      ┌────────────┐  │
│  │ dose hopper  │──────▶│ gate    │─────▶│ collection │  │
│  │ removable    │       │ + servo │      │ cup        │  │
│  └──────────────┘       └─────────┘      └────────────┘  │
│                                                          │
│  removable medication/contact tray                       │
├──────────────────────────────────────────────────────────┤
│  rear electronics bay: ESP32, power, buzzer MOSFET       │
│  rear cable entry                         lid sensor     │
└──────────────────────────────────────────────────────────┘
```

Top/side layout rules:

- Put medication-contact surfaces in a removable insert or hopper.
- Keep the servo and gate physically above the collection cup, not above the
  ESP32 bay.
- Put the lid microswitch near the hinge, where the lid has a repeatable stop.
- Mount the servo on a rigid bracket with two screws and a positive linkage
  stop. Do not rely on thin printed walls alone.
- Make the gate default closed by geometry, gravity, or a return spring. The
  servo must not be the only thing preventing free fall.
- Add a removable jam-clear cover over the hopper/gate/chute.
- Keep the OLED, buttons, and LEDs outside the medication-contact volume.
- Provide cable strain relief for the servo, lid sensor, chute sensor, and USB
  supply.

## Dispensing sequence

The firmware (Part 2) should implement this sequence:

1. `IDLE`: gate is commanded closed; no remote command can dispense silently.
2. `DOSE_DUE`: OLED and buzzer request attention.
3. `WAITING_FOR_CONFIRM`: user presses the local confirm button.
4. `CHECK_LID`: lid must be in the expected safe position.
5. `DISPENSING`: servo moves to the calibrated dispense position once.
6. `WAITING_FOR_CHUTE`: optional chute sensor must transition within a timeout.
7. `CLOSE_GATE`: servo returns to the closed stop.
8. `DISPENSE_CONFIRMED`: record an object-passed event if the chute sensor
   confirmed it; otherwise record `DISPENSE_UNCONFIRMED`.
9. `FAULT`: stop movement and sound the alarm for jam, unexpected lid motion,
   servo timeout, sensor failure, or power interruption.

Never automatically repeat a dispense attempt after a jam or reset. The user
must inspect the mechanism and explicitly clear the fault. A successful chute
transition means only that an object passed the chute; it does not prove pill
identity, dose correctness, or ingestion.

## Electrical layout

```text
Certified 5 V adapter
        │
     F1 + reverse-polarity protection
        ├──────── protected 5 V logic rail ── ESP32 VIN / board regulator
        │                                      ├─ OLED 3.3 V I2C (21/22)
        │                                      ├─ lid sensor GPIO18
        │                                      ├─ buttons GPIO4/16/17
        │                                      ├─ buzzer MOSFET GPIO19
        │                                      └─ LEDs GPIO2/15
        │
        └─ F2 ── servo 5 V branch ── J6 servo power
                  C7 1000 µF near servo

GPIO23 ── 220 Ω optional ── servo signal
GPIO27 ◀──────────── optional chute confirmation sensor
All returns ───────────── common ground; servo/buzzer use star return
```

## Parts required for the dispensing revision

In addition to the existing ESP32, OLED, buttons, LEDs, buzzer, and protected
power parts, add:

- 5 V positional servo with known stall current; SG90-class is suitable for a
  very light gate prototype, while a metal-gear servo may be needed after load
  testing.
- Servo bracket, horn, linkage, and mechanical hard stops.
- Removable hopper with a one-dose gate or pocket.
- Chute and removable collection cup.
- Lid microswitch, Hall sensor, or reed switch. Use one as the primary lid
  sensor.
- Optional optical break-beam or chute flap sensor.
- F2 for the servo branch and C7 1000 µF bulk capacitor.
- Inert test objects matched to the gate geometry.

## What the product can and cannot verify

| Evidence | Supported? |
| --- | --- |
| Reminder sounded/displayed | Yes |
| Lid opened/closed | Yes, with lid sensor |
| Servo was commanded | Yes |
| Object passed chute | Yes, only with optional chute sensor |
| Correct medication identity | No |
| Exact dose for arbitrary pill shapes | No; must be mechanically validated for a specific object |
| Medication swallowed | No |

This distinction is important: the backend must not turn a servo movement or
lid opening into a clinical `DOSE_TAKEN` claim.

## Design completion status

The repository now contains the Part 1 electrical and mechanical design for the
servo dispensing revision. Remaining implementation work is:

- Finalize the exact servo, sensor, and pill/test-object dimensions.
- Update the OpenSCAD enclosure with the final hopper/gate/bracket dimensions.
- Implement ESP32 PWM, dispensing state machine, jam timeout, and persistence.
- Add backend event types for attempted, confirmed, unconfirmed, and faulted
  dispensing.
- Test brownout, jam, empty hopper, multiple-object, lid-open, and reset cases.
- Do not use real medication until the mechanism has been independently
  inspected and validated for the intended object and use case.
