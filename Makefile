.PHONY: install test run dashboard

install:
	python -m pip install --requirement requirements.txt

test:
	python -m pytest -q

run:
	python -m uvicorn meditrack.main:app --host 0.0.0.0 --port 8000

dashboard:
	python -m streamlit run dashboard/app.py
