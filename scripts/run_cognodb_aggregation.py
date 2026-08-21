import json
import time
from pathlib import Path

from src.connections.cognodb import CognoDBConnection
from src.benchmark.statistics import summarize_latencies


WARMUP_ITERATIONS = 20
MEASURED_ITERATIONS = 100

RESULT_FILE = Path(
    "results/cognodb/aggregation.json"
)


QUERY = """
MATCH (u:User)
RETURN u.bucket AS bucket, count(u) AS user_count
ORDER BY bucket
"""


def main():

    connection = CognoDBConnection()

    try:

        connection.verify_connectivity()

        print()
        print(
            "## CognoDB aggregation benchmark"
        )

        print(
            f"Warm-up iterations: "
            f"{WARMUP_ITERATIONS}"
        )

        print(
            f"Measured iterations: "
            f"{MEASURED_ITERATIONS}"
        )

        print()
        print("Running warm-up...")

        for _ in range(WARMUP_ITERATIONS):

            result = connection.execute_query(
                QUERY
            )

            if len(result) != 100:
                raise RuntimeError(
                    "Aggregation returned an unexpected "
                    f"number of buckets: {len(result)}"
                )

        print("Running measured queries...")

        latencies = []

        for _ in range(MEASURED_ITERATIONS):

            start = time.perf_counter()

            result = connection.execute_query(
                QUERY
            )

            elapsed_ms = (
                time.perf_counter() - start
            ) * 1000

            if len(result) != 100:
                raise RuntimeError(
                    "Aggregation returned an unexpected "
                    f"number of buckets: {len(result)}"
                )

            latencies.append(elapsed_ms)

        statistics = summarize_latencies(
            latencies
        )

        print()
        print(
            "## Aggregation results"
        )

        print(
            f"Iterations : "
            f"{statistics['iterations']}"
        )

        print(
            f"p50        : "
            f"{statistics['p50_ms']:.3f} ms"
        )

        print(
            f"p95        : "
            f"{statistics['p95_ms']:.3f} ms"
        )

        print(
            f"Mean       : "
            f"{statistics['mean_ms']:.3f} ms"
        )

        print(
            f"Min        : "
            f"{statistics['min_ms']:.3f} ms"
        )

        print(
            f"Max        : "
            f"{statistics['max_ms']:.3f} ms"
        )

        RESULT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output = {
            "database": "cognodb",
            "workload": "aggregation",
            "query": QUERY.strip(),
            "warmup_iterations": WARMUP_ITERATIONS,
            "measured_iterations": MEASURED_ITERATIONS,
            "result_buckets": len(result),
            "statistics": statistics,
        }

        RESULT_FILE.write_text(
            json.dumps(
                output,
                indent=2,
            ),
            encoding="utf-8",
        )

        print()
        print(
            f"Results written to: "
            f"{RESULT_FILE}"
        )

    finally:

        connection.close()


if __name__ == "__main__":
    main()