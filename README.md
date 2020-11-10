# dataplatform-probe
Monitoring service for dataplatform services and events

This application continuously sends events to the dataplatform pipeline to test the latency of the pipeline.
It requires [Pipenv](https://github.com/pypa/pipenv) to be installed.
## Development
Running this app requires these environment variables to be set:

| Name                   | Description                                                         |
| ---------------------- | ------------------------------------------------------------------- |
| AUTHORIZER_API         | URL to Authorizer Api                                               |
| KEYCLOAK_SERVER        | URL to the keycloak server to use                                   |
| WEBSOCKET_URL          | URL to the websocket to listen to                                   |
| WEBHOOK_TOKEN          | Token to use to authenticate with websocket                         |
| ORIGO_CLIENT_SECRET    | Client Secret of the keycloak client to use                         |
| ORIGO_CLIENT_ID        | Client ID of the keycloak client to use                             |
| ORIGO_ENVIRONMENT      | Which environment to run on(dev/prod)                               |
| KEYCLOAK_REALM         | Name of the keycloak realm to use                                   |
| AWS_XRAY_SDK_ENABLED   | Whether to use AWS XRAY SDK (true/false)                            |
| EVENT_INTERVAL_SECONDS | Number of seconds to wait before sending an event                   |
| MAX_CONSECUTIVE_ERRORS | Number of consecutive errors allowed when attempting to post events |

The [run.sh](run.sh) script provided sets these environment variables and starts the app. If you wish to use it,
make sure to edit it to include the missing environment variables (secrets and such).

A makefile with various commands is provided for convenience and to ease development. These are:

#### Install dependencies
`make init`
#### Format using black
`make format`
#### Show format diff using black
`make format-diff`
#### Lint using flake8
`make lint`
#### Run the app
`make run-app`
#### Execute the [run.sh](run.sh) script
`make run-script`

## Metrics
This app uses the [prometheus_client](https://github.com/prometheus/client_python) library to expose
metrics to Prometheus regarding pipeline latency through a http server on port 8000.

These metrics are:
- **probe_events_posted** (Counter): The count of events posted to the pipeline
- **probe_event_post_errors** (Counter): The count of errors experienced when posting events
- **probe_events_received** (Counter): The count of events received from the pipeline
- **probe_wrong_appid** (Counter): The count of events received with the wrong App ID(posted by another instance of probe)
- **probe_event_latency** (Gauge): The latency of the latest received event

## Dependencies
This application uses the following dependencies:
- [Pipenv](https://github.com/pypa/pipenv)
- [aws-xray-sdk](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-python.html)
- [origo-sdk-python](https://github.com/oslokommune/origo-sdk-python)
- [websocket_client](https://github.com/websocket-client/websocket-client)
- [prometheus-client](https://github.com/prometheus/client_python)
- [flake8](https://pypi.org/project/flake8/)
- [black](https://github.com/psf/black)
