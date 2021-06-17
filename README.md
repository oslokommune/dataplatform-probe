# dataplatform-probe
Monitoring service for dataplatform services and events.

This application continuously sends events to the dataplatform pipeline to test the latency of the pipeline.

## Metrics
This app uses the [prometheus_client](https://github.com/prometheus/client_python) library to expose
metrics to Prometheus regarding pipeline latency through a http server on port 8000.

| Name | Type | Description |
| --- | --- | --- |
| `probe_events_posted` | `Counter` | Number of events posted. |
| `probe_events_received` | `Counter` | Number of events received. |
| `probe_events_lost` | `Counter` | Number of events considered lost. |
| `probe_event_post_errors` | `Counter` | Number of errors that occurred while posting events. |
| `probe_event_latency` | `Gauge` | The latency of the latest received event. |
| `probe_events_missing_1m_share` | `Gauge` | Share of events missing last minute. |
| `probe_events_missing_3m_share` | `Gauge` | Share of events missing last 3 minutes. |
| `probe_events_missing_10m_share` | `Gauge` | Share of events missing last 10 minutes. |
| `probe_events_duplicates` | `Counter` | Number of duplicates received. |
| `probe_wrong_appid` | `Counter` | Number of events received with a mismatched app id. |


## Configuration

The app is configurable by setting the following environment variables (* = no default, i.e. required):

| Name | Description | Default |
| --- | --- | --- |
| `WEBSOCKET_URL`* | URL to the websocket to listen to | |
| `PROBE_WEBHOOK_TOKEN`* | Token to use to authenticate with websocket | |
| `PROBE_DATASET_ID`* | Dataset ID | |
| `PROBE_DATASET_VERSION` | Dataset version | `1` |
| `POST_EVENT_INTERVAL_SECONDS` | Interval in seconds between posting events | `10` |
| `POST_EVENT_RETRIES` | Number of retries when posting an event (SDK) | `3` |
| `MARK_EVENT_LOST_TIMEOUT_SECONDS` | Number of seconds after which an event is considered lost | `5 * 60` |
| `PURGE_EVENT_TIMEOUT_SECONDS` | Number of seconds after which an event is purged from memory | `15 * 60` |
| `CLEAN_EVENTS_INTERVAL_SECONDS` | Interval in seconds between cleaning the event list | `30` |

In addition, `OKDATA_CLIENT_ID`, `OKDATA_CLIENT_SECRET`, and `OKDATA_ENVIRONMENT`, must also be set when deploying.

## Development

A makefile with various commands is provided for convenience and to ease development. These are:

```sh
$ make init # Install dependencies
$ make format # Format using black
$ make lint # Lint using flake8
$ make run # Run application (as described below)
```

### Running

By issuing the command `make run`, a local environment is configured comprising of the following services (see `local-compose.yaml`):

| Service | Description | |
| --- | --- | --- |
| [Prometheus](https://hub.docker.com/r/prom/prometheus) | Monitoring and alerting toolkit. | `http://localhost:9090` |
| [Grafana](https://hub.docker.com/r/grafana/grafana) (+ [tns-db](https://hub.docker.com/r/grafana/tns-db)) | Observability and data visualization platform. Includes a provisioned datasource and dashboard for the application. Default username/password: `admin`/`admin`. | `http://localhost:3000` |
| WebSocket server | Simply echoes received events to connected clients (emulating [event-data-subscription](https://github.com/oslokommune/event-data-subscription).) | `ws://localhost:8765` |
| HTTP server | Accepts post requests for events (emulating [okdata-event-collector](https://github.com/oslokommune/okdata-event-collector)). By default configured to introduce some (more or less random) latency (between 0-3 seconds) for ~10 percent of received events, and simply "losing" ~5 percent (configurable at `http://localhost:8081/config/` by passing query arguments, e.g. `?ADD_LATENCY_PERCENT=15`). | `http://localhost:8081` |

The `run` target sets `RUN_LOCAL=true` and `LOCAL_SERVICES_ONLY=true`. While the first environment variable enables "debug mode", the latter tells the application to bypasss connections to `event-collector`/`event-data-subscription` and instead use the "dummy" WebSocket/HTTP servers mentioned above. Also: When running the application locally, an additonal task is created which simply prints a table of all tracked events every 30 seconds.

To test against `event-collector`/`event-data-subscription` "for real" (while stilling running the application locally), set the appropriate environment variables listed above (i.e. credentials, dataset id, webhook token) and use `make run-dp`.

```sh
$ docker-compose -f local-compose.yaml ps # Check services
$ docker-compose -f local-compose.yaml logs --follow --tail=10 # Tail service logs
```

## Deploy

TODO
