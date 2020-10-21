#!/usr/bin/bash
export AUTHORIZER_API=https://api.data-dev.oslo.systems/simple-dataset-authorizer
export KEYCLOAK_SERVER=https://login-test.oslo.kommune.no
export WEBSOCKET_URL=wss://ws.data-dev.oslo.systems/event-data-subscription
export WEBHOOK_TOKEN=XXXXXXXXX
export ORIGO_CLIENT_SECRET=XXXXXXXXXXX
export ORIGO_CLIENT_ID=dataplatform-monitoring
export ORIGO_ENVIRONMENT=dev
export KEYCLOAK_REALM=api-catalog
export AWS_XRAY_SDK_ENABLED=false
export EVENT_INTERVAL_SECONDS=15
export MAX_CONSECUTIVE_ERRORS=3
python probe/run_probe.py
