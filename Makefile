compile-requirements:
	pip-compile -o requirements/base.txt requirements/base.in
	pip-compile -o requirements/development.txt requirements/development.in
	pip-compile -o requirements/testing.txt requirements/testing.in
