.PHONY: install test hardware-test run dashboard

PYTHON ?= python3

install:
	$(PYTHON) -m pip install --requirement requirements.txt

test:
	$(PYTHON) -m pytest -q

hardware-test:
	$(PYTHON) hardware/validation/part1_validate.py

run:
	$(PYTHON) -m uvicorn meditrack.main:app --host 0.0.0.0 --port 8000

dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py
