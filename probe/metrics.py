from prometheus_client import Counter, Gauge


class Metrics:
    tasks_created: Counter = Counter(
        name="probe_tasks_created",
        documentation="Number of created tasks",
        labelnames=["app_id"],
    )
    tasks_succeeded: Counter = Counter(
        name="probe_tasks_succeeded",
        documentation="Number of succeeded tasks",
        labelnames=["app_id"],
    )
    tasks_failed: Counter = Counter(
        name="probe_tasks_failed",
        documentation="Number of failed tasks",
        labelnames=["app_id"],
    )
    task_duration: Gauge = Gauge(
        name="probe_task_duration", documentation="Task duration"
    )
