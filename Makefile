 ifeq (, $(shell which pipenv))
 $(error "Pipenv not found in PATH. Install here: https://github.com/pypa/pipenv#installation")
 endif

.PHONY: run-script
run-script:
	pipenv run script

.PHONY: run-app
run-app:
	pipenv run app

.PHONY: init
init:
	pipenv install

.PHONY: clean
clean:
	pipenv clean

.PHONY: lint
lint:
	pipenv run flake8

.PHONY: format-diff
format-diff:
	pipenv run black-diff

.PHONY: format
format:
	pipenv run black