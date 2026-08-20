import statistics


def percentile(values, percentile):
    """Calculate a percentile using linear interpolation."""

    if not values:
        raise ValueError(
            "Cannot calculate percentile from empty data."
        )

    sorted_values = sorted(values)

    index = (
        (len(sorted_values) - 1)
        * percentile
        / 100
    )

    lower = int(index)
    upper = min(
        lower + 1,
        len(sorted_values) - 1,
    )

    fraction = index - lower

    return (
        sorted_values[lower]
        + (
            sorted_values[upper]
            - sorted_values[lower]
        )
        * fraction
    )


def summarize_latencies(latencies):
    """Return benchmark latency statistics in milliseconds."""

    if not latencies:
        raise ValueError(
            "No latency measurements available."
        )

    return {
        "iterations": len(latencies),
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "mean_ms": statistics.mean(latencies),
        "stdev_ms": (
            statistics.stdev(latencies)
            if len(latencies) > 1
            else 0
        ),
        "p50_ms": percentile(
            latencies,
            50,
        ),
        "p95_ms": percentile(
            latencies,
            95,
        ),
    }