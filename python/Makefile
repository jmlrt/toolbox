VENV := $(HOME)/.venvs/tools

.PHONY: venv
venv:
	python3 -m venv $(VENV)

.PHONY: pip
pip: venv
	$(VENV)/bin/pip install -qr requirements.txt

*.py: pip
	$(VENV)/bin/python3 $@ $(ARGS)

.PHONY: lint
lint: pip
	$(VENV)/bin/flake8 .

.PHONY: format
format: pip
	$(VENV)/bin/black .

.PHONY: test
test: pip
	$(VENV)/bin/pytest tests

.PHONY: ipython
ipython: pip
	$(VENV)/bin/ipython
