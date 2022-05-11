# dataplatform-probe
Monitoring service for dataplatform services and events.

## Metrics
This app uses the [prometheus_client](https://github.com/prometheus/client_python) library to expose
metrics to Prometheus regarding pipeline latency through a http server on port `8000`.

| Name                             | Type      | Description                                          |
|----------------------------------|-----------|------------------------------------------------------|
| `probe_tasks_created`            | `Counter` | Number of created tasks.                             |
| `probe_tasks_succeeded`          | `Counter` | Number of succeeded tasks.                           |
| `probe_tasks_failed`             | `Counter` | Number of failed tasks.                              |
| `probe_task_duration`            | `Gauge`   | The duration of the last succeeded task.             |

## Configuration

The app is configurable by setting the following environment variables (* = required, no default):

| Name                           | Description                                                      | Default        |
|--------------------------------|------------------------------------------------------------------|----------------|
| `DATASET_ID`*                  | Dataset ID                                                       |                |
| `TASK_INTERVAL_SECONDS`        | Interval in seconds between creating a new task                  | `10`           |
| `DISMISS_TASK_SECONDS`         | Seconds after which a task is removed                            | `60 * 60 * 24` |
| `CLEAN_TASKS_INTERVAL_SECONDS` | Interval in seconds between cleaning the task backlog            | `60 * 5`       |

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

* [**Prometheus**](https://hub.docker.com/r/prom/prometheus) | `http://localhost:9090` \
  Monitoring and alerting toolkit.

* [**Grafana**](https://hub.docker.com/r/grafana/grafana) (+ [tns-db](https://hub.docker.com/r/grafana/tns-db)) | `http://localhost:3000`  \
  Observability and data visualization platform. Includes a provisioned datasource and dashboard for the application. Default username/password: `admin`/`admin`.

* **HTTP server** | `http://localhost:8081` \
  Accepts requests from tasks, currently emulating [okdata-metadata-api](https://github.com/oslokommune/okdata-metadata-api). By default configured to introduce some (more or less random) latency (between 0-3 seconds) for ~10 percent of requests, as well as failing with `401` for ~5 percent (configurable in `local/http_server/http_server.py`).

The `run` target sets `LOCAL_RUN=true` and `LOCAL_SERVICES_ONLY=true`. While the first environment variable enables "debug mode", the latter tells the application to use the "dummy" HTTP server mentioned above. Also: When running the application locally, an additonal task is created which simply prints a table of all tracked tasks every 30 seconds.

To test against real dataplatform services (while still running the application locally), set the appropriate environment variables listed above (i.e. credentials and dataset id) and use `make run-dp`.

```sh
$ docker-compose -f local-compose.yaml ps # Check services
$ docker-compose -f local-compose.yaml logs --follow --tail=10 # Tail service logs
```

## Deploy

Deploy to both dev and prod is automatic via GitHub Actions on push to master.
