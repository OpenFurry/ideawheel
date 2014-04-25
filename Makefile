SQLITE=sqlite3
LOCAL_DB=ideawheel.db
DB_SCHEMA=schema.sql

help:
	@echo 'Usage:'
	@echo '   make deps       installs dependencies'
	@echo '   make basedb     sets up an empty local database'
	@echo '   make devserver  starts the development server'
	@echo '   make check      run tests and lint'
	@echo '   make test       run the tests'
	@echo '   make lint       run flake8 for pep8 linting'
	@echo '   make clean      removes compiled files'
	@echo '   make help       displays this message'

deps:
	pip install -r dev-requirements.txt

basedb: $(LOCAL_DB)

$(LOCAL_DB): $(DB_SCHEMA)
	rm -f $(LOCAL_DB)
	$(SQLITE) $(LOCAL_DB) < $(DB_SCHEMA)

devserver:
	python ideawheel.py

devfixtures: basedb
	for i in `find fixtures/dev/*.sql | sort`; do $(SQLITE) $(LOCAL_DB) < $$i; done

check: test lint

test:
	@nosetests --verbosity=2 --with-coverage --cover-package=ideawheel,models,views
	@rm .coverage

lint:
	@flake8 --show-source .

clean:
	find . -name '*.py[co]' -exec rm -f {} \;

.PHONY: help deps basedb devfixtures devserver check test lint clean
