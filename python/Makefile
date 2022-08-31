ifeq ($(VIRTUAL_ENV),)
	VIRTUAL_ENV := $(HOME)/.venvs/tools
endif

.PHONY: clean
clean: ## Clean python environment
	find . -type d -name '.pytest_cache' -prune -exec rm -fr {} \;
	find . -type d -name __pycache__ -prune -exec rm -fr {} \;
	find . -type d -name '*.egg-info' -prune -exec rm -fr {} \;
	find . -type d -name 'dist' -prune -exec rm -fr {} \;

.PHONY: venv
venv:
	python3 -m venv $(VIRTUAL_ENV)

.PHONY: pip
pip: venv
	$(VIRTUAL_ENV)/bin/pip install --upgrade pip
	$(VIRTUAL_ENV)/bin/pip install -qr requirements.txt

*.py: pip
	$(VIRTUAL_ENV)/bin/python3 $@ $(ARGS)

.PHONY: lint
lint: pip
	$(VIRTUAL_ENV)/bin/flake8 .

.PHONY: format
format: pip
	$(VIRTUAL_ENV)/bin/black .
	$(VIRTUAL_ENV)/bin/isort .

.PHONY: test
test: pip
	$(VIRTUAL_ENV)/bin/pytest -lsvx \
		--cov-report term-missing \
		--random-order-bucket=global \
		tests $(ARGS)

.PHONY: ipython
ipython: pip
	$(VIRTUAL_ENV)/bin/ipython
