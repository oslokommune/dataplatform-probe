#!/usr/bin/bash
export AUTHORIZER_API=https://api.data-dev.oslo.systems/simple-dataset-authorizer
export KEYCLOAK_SERVER=https://login-test.oslo.kommune.no
export WEBSOCKET_URL=wss://ws.data-dev.oslo.systems/event-data-subscription
export WEBHOOK_TOKEN=XXXXXXXXX
export OKDATA_CLIENT_SECRET=XXXXXXXXXXX
export OKDATA_CLIENT_ID=XXXXXXXXXXXX
export OKDATA_ENVIRONMENT=dev
export KEYCLOAK_REALM=XXXXXXXXX
export AWS_XRAY_SDK_ENABLED=false
export EVENT_INTERVAL_SECONDS=15
export DATASET_ID=XXXXXXXXX
python probe/run_probe.py
