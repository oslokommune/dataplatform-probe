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

* [Prometheus](https://hub.docker.com/r/prom/prometheus)
* [Grafana](https://hub.docker.com/r/grafana/grafana) (including [tns-db](https://hub.docker.com/r/grafana/tns-db) and provisioned datasource and dashboard for the application)
* A websocket server that simply echoes received events to connected clients (emulating [event-data-subscription](https://github.com/oslokommune/event-data-subscription))
* A web server which accepts post requests for events (emulating [okdata-event-collector](https://github.com/oslokommune/okdata-event-collector))

By specifying `LOCAL_SERVICES_ONLY=true` when running the application (e.g. `LOCAL_SERVICES_ONLY=true make run`), the application bypasses connections to `event-collector`/ `event-data-subscription` and is instead configured to use the "dummy" WebSocket/HTTP servers. 

The HTTP server is by default configured to introduce some (more or less random) latency (between 0-3 seconds) for ~10 percent of received events, and simply "losing" ~5 percent (configurable at `http://localhost:8081/config/` by passing query arguments, e.g. `?ADD_LATENCY_PERCENT=15`). Also: When running the application locally, an additonal task is created which simply prints a table of all tracked events every 30 seconds.

To "tail" the service logs:
```sh
$ docker-compose -f local-compose.yaml logs --follow --tail=10
```

## Deploy

TODO
