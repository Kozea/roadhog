include Makefile.config
-include Makefile.custom.config

all: install serve

install:
	test -d $(VENV) || virtualenv -p python3.6 $(VENV)
	$(PIP) install --upgrade --no-cache pip setuptools -e .[test]

install-dev:
	$(PIP) install --upgrade devcore

clean:
	rm -fr dist

clean-install: clean
	rm -fr $(VENV)
	rm -fr *.egg-info

lint:
	$(PYTEST) --no-cov --flake8 -m flake8
	$(PYTEST) --no-cov --isort -m isort

check-python:
	TESTING_SETTINGS=$(FLASK_TEST_CONFIG) $(PYTEST) -vv $(PROJECT_NAME)

check-outdated:
	$(PIP) list --outdated --format=columns

check: check-python check-outdated
