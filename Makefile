SQLITE=sqlite3
LOCAL_DB=ideawheel.db
DB_SCHEMA=schema.sql

help:
	@echo 'Usage:'
	@echo '   make deps       installs dependencies'
	@echo '   make basedb     sets up an empty local database'
	@echo '   make devserver  starts the development server'
	@echo '   make test       run the tests'
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

test:
	python ideawheel_tests.py

clean:
	find . -name '*.py[co]' -exec rm -f {} \;

.PHONY: help deps clean devserver basedb
