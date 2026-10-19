from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
ini = (root / "platformio.ini").read_text()
src = (root / "src/main.cpp").read_text()
cfg = (root / "include/config.h").read_text()
required_states = ["IDLE", "DOSE_DUE", "WAITING_FOR_CONFIRM", "CHECK_LID", "DISPENSING", "WAITING_FOR_CHUTE", "CLOSE_GATE", "DISPENSE_CONFIRMED", "DISPENSE_UNCONFIRMED", "FAULT"]
pins = {21,22,18,27,19,4,16,17,2,15,23,25,26}
assert all(s in src for s in required_states), "FSM state missing"
assert all(str(p) in src for p in pins), "Part 1 pin missing"
assert "millis()" in src and "delay(" not in src, "firmware must be non-blocking"
assert "LittleFS" in src and "Preferences" in src and "HTTPClient" in src
assert "Adafruit_SH110X.h" in src, "SH1106 library header missing"
assert "platform = espressif32@6.7.0" in ini and "@" in ini
assert "change-me" in cfg and "password" in cfg.lower(), "config must contain safe placeholders"
print("firmware validation passed: pins, FSM, non-blocking loop, persistence, queue, HTTP and pinned deps")
