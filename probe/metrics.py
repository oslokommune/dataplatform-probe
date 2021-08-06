from prometheus_client import Counter, Enum, Gauge


class Metrics:
    connection_state: Enum = Enum(
        name="probe_connection_state",
        states=["connected", "disconnected"],
        documentation="WebSocket connection state",
    )

    events_posted: Counter = Counter(
        name="probe_events_posted",
        documentation="Number of events posted",
        labelnames=["app_id"],
    )
    events_received: Counter = Counter(
        name="probe_events_received",
        documentation="Number of events received",
        labelnames=["app_id"],
    )
    events_lost: Counter = Counter(
        name="probe_events_lost",
        documentation="Number of events considered lost",
        labelnames=["app_id"],
    )
    event_post_errors: Counter = Counter(
        name="probe_event_post_errors",
        documentation="Number of errors that occurred while posting events",
        labelnames=["app_id"],
    )
    event_latency: Gauge = Gauge(
        name="probe_event_latency", documentation="Event latency"
    )

    events_missing_1m_share = Gauge(
        name="probe_events_missing_1m_share",
        documentation="Share of events missing last 1 minute",
    )
    events_missing_10m_share = Gauge(
        name="probe_events_missing_10m_share",
        documentation="Share of events missing last 10 minutes",
    )
    events_missing_1h_share = Gauge(
        name="probe_events_missing_1h_share",
        documentation="Share of events missing last 1 hour",
    )

    events_duplicates: Counter = Counter(
        name="probe_events_duplicates",
        documentation="Number of duplicates received",
        labelnames=["app_id"],
    )
    wrong_appid_count: Counter = Counter(
        name="probe_wrong_appid",
        documentation="Number of events received with a mismatched app id",
        labelnames=["app_id"],
    )
