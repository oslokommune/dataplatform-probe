# dataplatform-probe
Monitoring service for dataplatform services.

Continuously requests access tokens from Keycloak using the client credentials grant in order to keep an eye on it.

## Metrics
This app uses the [prometheus_client](https://github.com/prometheus/client_python) library to expose
metrics to Prometheus regarding request latency through a http server on port `8000`.

| Name                       | Type      | Description                                 |
|----------------------------|-----------|---------------------------------------------|
| `probe_requests_created`   | `Counter` | Number of created requests                  |
| `probe_requests_succeeded` | `Counter` | Number of succeeded requests                |
| `probe_requests_failed`    | `Counter` | Number of failed requests                   |
| `probe_request_duration`   | `Gauge`   | The duration of the last succeeded requests |

## Configuration

The app is configurable by setting the following environment variables (* = required, no default):

| Name                         | Description                                                  | Default |
|------------------------------|--------------------------------------------------------------|---------|
| `KEYCLOAK_SERVER_URL`*       | Keycloak base URL, e.g. `https://login.oslo.kommune.no/auth` |         |
| `KEYCLOAK_REALM`*            | Keycloak realm, e.g. `api-catalog`                           |         |
| `KEYCLOAK_CLIENT_ID`*        | Client ID used for the client credentials grant              |         |
| `KEYCLOAK_CLIENT_SECRET`*    | Client secret used for the client credentials grant          |         |
| `TASK_INTERVAL_SECONDS`      | Interval in seconds between requests                         | `30`    |
| `REQUEST_TIMEOUT_SECONDS`    | Timeout in seconds for each request                          | `10`    |
| `BETTERUPTIME_HEARTBEAT_URL` | Send heartbeat to Better Uptime on successful task execution |         |

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

* [**Prometheus**](https://hub.docker.com/r/prom/prometheus) | `http://localhost:9090` \
  Monitoring and alerting toolkit.

* [**Grafana**](https://hub.docker.com/r/grafana/grafana) (+ [tns-db](https://hub.docker.com/r/grafana/tns-db)) | `http://localhost:3000`  \
  Observability and data visualization platform. Includes a provisioned datasource and dashboard for the application. Default username/password: `admin`/`admin`.

* **HTTP server** | `http://localhost:8081` \
  Accepts requests from tasks, emulating the Keycloak token endpoint. By default configured to introduce some (more or less random) latency (between 0-3 seconds) for ~10 percent of requests, as well as failing with `401` for ~5 percent (configurable in `local/http_server/http_server.py`).

The `run` target sets `LOCAL_RUN=true`, which enables "debug mode", and points the application at the "dummy" HTTP server mentioned above.

To test against a real Keycloak instance (while still running the application locally), set the environment variables listed above and use `make run-keycloak`.

```sh
$ docker compose -f local-compose.yaml ps # Check services
$ docker compose -f local-compose.yaml logs --follow --tail=10 # Tail service logs
```

## Deploy

Deploy to both dev and prod is automatic via GitHub Actions on push to master.
