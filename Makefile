.PHONY: install test hardware-test run dashboard

# Prefer the repository-local environment so `make test` is reproducible after
# the README setup. Callers may still override this with `make PYTHON=...`.
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

install:
	$(PYTHON) -m pip install --requirement requirements.txt

test:
	$(PYTHON) -m pytest -q
	$(PYTHON) firmware/esp32_meditrack/tools/validate_firmware.py

hardware-test:
	$(PYTHON) hardware/validation/part1_validate.py

run:
	$(PYTHON) -m uvicorn meditrack.main:app --host 0.0.0.0 --port 8000

dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py
