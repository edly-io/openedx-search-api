compile-requirements:
	pip-compile -o requirements/base.txt requirements/base.in
	pip-compile -o requirements/development.txt requirements/development.in
	pip-compile -o requirements/testing.txt requirements/testing.in

# Note that we only run a subset of tests for now, because other tests require a running
# meilisearch instance.
test-unit:
	./manage.py test --settings=openedx_search.settings.test openedx_search_api.tests.test_engine
