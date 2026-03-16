"""
Prometheus metrics for application monitoring.

Provides counters and histograms for tracking:
- HTTP request metrics
- Database operation metrics
- External API call metrics
- Background job metrics
"""

import time
from functools import wraps
from typing import Callable

from prometheus_client import Counter, Gauge, Histogram

# HTTP request metrics
http_requests_total = Counter(
    "dualstack_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "dualstack_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

# Database operation metrics
db_operations_total = Counter(
    "dualstack_db_operations_total",
    "Total database operations",
    ["operation", "table", "status"],
)

# External API call metrics
external_api_calls_total = Counter(
    "dualstack_external_api_calls_total",
    "Total external API calls",
    ["service", "operation", "status"],
)

# Background job metrics
background_job_duration_seconds = Histogram(
    "dualstack_background_job_duration_seconds",
    "Background job execution duration",
    ["job_name"],
    buckets=[0.1, 0.5, 1, 5, 10, 30, 60, 120],  # 0.1s to 2 minutes
)

background_job_executions_total = Counter(
    "dualstack_background_job_executions_total",
    "Total background job executions",
    ["job_name", "status"],  # success/failure
)

background_job_failures_total = Counter(
    "dualstack_background_job_failures_total",
    "Total background job failures",
    ["job_name", "error_type"],
)

background_job_last_success = Gauge(
    "dualstack_background_job_last_success_timestamp",
    "Timestamp of last successful job run",
    ["job_name"],
)

# Database connection pool metrics
db_connection_pool_size = Gauge(
    "dualstack_db_connection_pool_size",
    "Total number of connections in the pool",
)

db_connection_pool_checked_out = Gauge(
    "dualstack_db_connection_pool_checked_out",
    "Number of connections currently checked out",
)

db_connection_pool_overflow = Gauge(
    "dualstack_db_connection_pool_overflow",
    "Number of overflow connections",
)

db_query_duration_seconds = Histogram(
    "dualstack_db_query_duration_seconds",
    "Database query execution duration",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5],  # 1ms to 5s
)


def increment_http_requests(method: str, endpoint: str, status_code: int) -> None:
    """Increment HTTP request counter."""
    http_requests_total.labels(
        method=method, endpoint=endpoint, status_code=status_code
    ).inc()


def observe_http_duration(method: str, endpoint: str, duration: float) -> None:
    """Observe HTTP request duration."""
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(
        duration
    )


def increment_db_operations(operation: str, table: str, status: str) -> None:
    """Increment database operation counter."""
    db_operations_total.labels(operation=operation, table=table, status=status).inc()


def increment_external_api_calls(service: str, operation: str, status: str) -> None:
    """Increment external API call counter."""
    external_api_calls_total.labels(
        service=service, operation=operation, status=status
    ).inc()


def _record_job_success(job_name: str, duration: float) -> None:
    """Record metrics for a successful background job execution."""
    from app.core.logging import get_logger

    background_job_duration_seconds.labels(job_name=job_name).observe(duration)
    background_job_executions_total.labels(job_name=job_name, status="success").inc()
    background_job_last_success.labels(job_name=job_name).set(time.time())

    get_logger(__name__).info(
        "background_job_completed",
        job_name=job_name,
        duration_seconds=duration,
        status="success",
    )


def _record_job_failure(job_name: str, duration: float, exc: Exception) -> None:
    """Record metrics for a failed background job execution."""
    from app.core.logging import get_logger

    error_type = type(exc).__name__
    background_job_duration_seconds.labels(job_name=job_name).observe(duration)
    background_job_executions_total.labels(job_name=job_name, status="failure").inc()
    background_job_failures_total.labels(job_name=job_name, error_type=error_type).inc()

    get_logger(__name__).error(
        "background_job_failed",
        job_name=job_name,
        duration_seconds=duration,
        error_type=error_type,
        error=str(exc),
    )


def track_job_metrics(job_name: str) -> Callable:
    """Decorator to track background job metrics.

    Usage:
        @track_job_metrics("data_sync")
        async def run_data_sync():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                _record_job_success(job_name, time.time() - start_time)
                return result
            except Exception as e:
                _record_job_failure(job_name, time.time() - start_time, e)
                raise

        return wrapper

    return decorator


def update_pool_metrics() -> None:
    """Update database connection pool metrics."""
    from app.core.database import get_engine

    engine = get_engine()
    if engine is None:
        return

    pool = engine.pool
    if not hasattr(pool, "size"):
        return

    db_connection_pool_size.set(pool.size())
    db_connection_pool_checked_out.set(pool.checkedout())
    db_connection_pool_overflow.set(pool.overflow())
