VENV := $(HOME)/.venvs/tools

.PHONY: clean
clean: ## Clean python environment
	find . -type d -name '.pytest_cache' -prune -exec rm -fr {} \;
	find . -type d -name __pycache__ -prune -exec rm -fr {} \;
	find . -type d -name '*.egg-info' -prune -exec rm -fr {} \;
	find . -type d -name 'dist' -prune -exec rm -fr {} \;

.PHONY: venv
venv:
	python3 -m venv $(VENV)

.PHONY: pip
pip: venv
	$(VENV)/bin/pip install --upgrade pip
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
	$(VENV)/bin/pytest -lsvx \
		--cov-report term-missing \
		--random-order-bucket=global \
		tests $(ARGS)

.PHONY: ipython
ipython: pip
	$(VENV)/bin/ipython
