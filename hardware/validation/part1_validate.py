"""Offline consistency checks for the Part 1 hardware artifacts."""

from csv import DictReader
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    pinout = list(DictReader((ROOT / "wiring/pinout.csv").open(newline="")))
    by_net = {row["net"]: row for row in pinout}
    expected = {
        "I2C_SDA": "21",
        "I2C_SCL": "22",
        "COMPARTMENT_SENSE": "18",
        "BUZZER_GATE": "19",
        "SERVO_CYLINDER_1": "23",
        "SERVO_CYLINDER_2": "25",
        "SERVO_CYLINDER_3": "26",
        "DISPENSE_CONFIRM": "27",
        "BTN_CONFIRM": "4",
        "BTN_MUTE_SNOOZE": "16",
        "BTN_SNOOZE": "17",
        "LED_GREEN": "2",
        "LED_RED": "15",
    }
    assert set(expected) <= by_net.keys()
    for net, gpio in expected.items():
        assert by_net[net]["esp32_gpio"] == gpio, (net, by_net[net])

    bom_text = (ROOT / "bom/meditrack_bom.csv").read_text()
    assert "servo motors" in bom_text
    assert "Normally-open lever switch" in bom_text

    diagram = (ROOT / "schematics/meditrack_block_diagram.svg").read_text()
    for required in ("GPIO21", "GPIO22", "GPIO19", "GPIO18"):
        assert required in diagram

    for required_file in (
        ROOT / "README.md",
        ROOT / "wiring/point_to_point_wiring.md",
        ROOT / "validation/power_budget.md",
        ROOT / "enclosure/meditrack_enclosure.scad",
    ):
        assert required_file.exists(), required_file

    print(f"validated {len(pinout)} pinout nets and Part 1 artifact set")


if __name__ == "__main__":
    main()
