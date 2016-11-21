SQLITE=sqlite3
LOCAL_DB=ideawheel.db
DB_SCHEMA=schema.sql
VIRTUALENV=venv

help:
	@echo 'Usage:'
	@echo '   make deps		installs dependencies'
	@echo '   make basedb		sets up an empty local database'
	@echo '   make devserver	starts the development server in tox (py35)'
	@echo '   make check		run tests and lint in tox (py27 and py35)'
	@echo '   make rawdevserver	starts the development server in a virtualenv'
	@echo '   make rawcheck		run tests and lint in a virtualenv'
	@echo '   make rawtest		run the tests in a virtualenv'
	@echo '   make rawlint		run flake8 for pep8 linting in a virtualenv'
	@echo '   make clean		removes compiled files and virtual environments'
	@echo '   make help		displays this message'

deps: $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -r requirements.txt

basedb: $(LOCAL_DB)

$(LOCAL_DB): $(DB_SCHEMA)
	rm -f $(LOCAL_DB)
	$(SQLITE) $(LOCAL_DB) < $(DB_SCHEMA)

check:
	tox

devserver:
	tox -e devenv

rawdevserver: $(VIRTUALENV)
	$(VIRTUALENV)/bin/python ideawheel.py

devfixtures: basedb
	for i in `find fixtures/dev/*.sql | sort`; do $(SQLITE) $(LOCAL_DB) < $$i; done

rawcheck: rawlint rawtest

rawtest: $(VIRTUALENV)
	@$(VIRTUALENV)/bin/coverage erase
	@$(VIRTUALENV)/bin/nosetests --verbosity=2 --with-coverage --cover-package=ideawheel,models,views

rawlint: $(VIRTUALENV)
	@$(VIRTUALENV)/bin/flake8 --config=tox.ini

clean:
	rm -rf .tox $(VIRTUALENV)
	find . -name '*.py[co]' -exec rm -f {} \;

$(VIRTUALENV):
	virtualenv $(VIRTUALENV)

.PHONY: help deps basedb devfixtures devserver check test lint rawdevserver rawcheck rawtest rawlint clean
