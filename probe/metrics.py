from prometheus_client import Counter, Gauge


class Metrics:
    requests_created: Counter = Counter(
        name="probe_requests_created",
        documentation="Number of created requests",
        labelnames=["app_id"],
    )
    requests_succeeded: Counter = Counter(
        name="probe_requests_succeeded",
        documentation="Number of succeeded requests",
        labelnames=["app_id"],
    )
    requests_failed: Counter = Counter(
        name="probe_requests_failed",
        documentation="Number of failed requests",
        labelnames=["app_id"],
    )

    request_duration: Gauge = Gauge(
        name="probe_request_duration", documentation="Request duration"
    )
