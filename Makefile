.DEV_PROFILE := okdata-dev
.PROD_PROFILE := okdata-prod

GLOBAL_PY := python3
BUILD_VENV ?= .build_venv
BUILD_PY := $(BUILD_VENV)/bin/python

.PHONY: init
init: $(BUILD_VENV)

$(BUILD_VENV):
	$(GLOBAL_PY) -m venv $(BUILD_VENV)
	$(BUILD_PY) -m pip install -U pip
	$(BUILD_PY) -m pip install -r requirements.txt

.PHONY: format
format: $(BUILD_VENV)/bin/black
	$(BUILD_PY) -m black .

.PHONY: lint
lint: $(BUILD_VENV)/bin/flake8
	$(BUILD_VENV)/bin/flake8 --ignore E501 probe/

.PHONY: upgrade-deps
upgrade-deps: $(BUILD_VENV)/bin/pip-compile
	$(BUILD_VENV)/bin/pip-compile -U

setup-local-env:
	docker-compose \
		-f local-compose.yaml \
		up -d

tear-down-local-env:
	docker-compose \
		-f local-compose.yaml \
		down -v --remove-orphans || true

stop-local-env:
	docker-compose \
		-f local-compose.yaml \
		stop

.PHONY: run
run: setup-local-env
	LOCAL_RUN=true \
	LOCAL_SERVICES_ONLY=true \
	DATASET_ID=abc123 \
	WEBHOOK_TOKEN=abc123 \
	DISMISS_EVENT_TIMEOUT_SECONDS=300 \
	CLEAN_EVENTS_INTERVAL_SECONDS=60 \
	$(BUILD_VENV)/bin/python -m probe

.PHONY: run-dp
run-dp: setup-local-env
	LOCAL_RUN=true \
	LOCAL_SERVICES_ONLY=false \
	$(BUILD_VENV)/bin/python -m probe


###
# Python build dependencies
##

$(BUILD_VENV)/bin/pip-compile: $(BUILD_VENV)
	$(BUILD_PY) -m pip install -U pip-tools

$(BUILD_VENV)/bin/%: $(BUILD_VENV)
	$(BUILD_PY) -m pip install -U $*
