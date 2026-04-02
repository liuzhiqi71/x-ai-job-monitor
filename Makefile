PYTHON ?= python3

.PHONY: test check-secrets run

test:
	$(PYTHON) -m pytest

check-secrets:
	$(PYTHON) scripts/check_secrets.py .

run:
	$(PYTHON) -m x_job_monitor run --config config.example.yaml

