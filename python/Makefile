venv:
	python3 -m venv venv

.PHONY: pip
pip: venv
	venv/bin/pip install -qr requirements.txt
	venv/bin/pip install -qr test-requirements.txt

*.py: pip
	venv/bin/python3 $@ $(ARGS)

.PHONY: lint
lint: pip
	venv/bin/flake8 *.py

.PHONY: format
format: pip
	venv/bin/black *.py

.PHONY: ipython
ipython: pip
	venv/bin/ipython

.PHONY: clean
clean:
	rm -fr venv

