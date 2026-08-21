import random
from pathlib import Path

from src.connections.cognodb import CognoDBConnection
from src.benchmark.statistics import summarize_latencies


WARMUP_ITERATIONS = 20
MEASURED_ITERATIONS = 100

RESULT_FILE = Path(
    "results/cognodb/filtered_lookup.json"
)


QUERY = """
MATCH (u:User)
WHERE u.bucket = $bucket
RETURN count(u) AS user_count
"""


def main():

    connection = CognoDBConnection()

    try:

        connection.verify_connectivity()

        print()
        print(
            "## CognoDB indexed/filtered lookup benchmark"
        )

        print(
            f"Warm-up iterations: "
            f"{WARMUP_ITERATIONS}"
        )

        print(
            f"Measured iterations: "
            f"{MEASURED_ITERATIONS}"
        )

        buckets = list(range(100))

        print()
        print("Running warm-up...")

        for _ in range(WARMUP_ITERATIONS):

            bucket = random.choice(buckets)

            connection.execute_query(
                QUERY,
                {"bucket": bucket},
            )

        print("Running measured queries...")

            # The query result is intentionally consumed
            # so that the full database operation completes.

            # We measure only the client-observed query
            # execution time below.


        # Re-run the measured workload with timing.
        latencies = []

        import time

        for _ in range(MEASURED_ITERATIONS):

            bucket = random.choice(buckets)

            start = time.perf_counter()

            result = connection.execute_query(
                QUERY,
                {"bucket": bucket},
            )

            elapsed_ms = (
                time.perf_counter() - start
            ) * 1000

            if not result:
                raise RuntimeError(
                    "Filtered lookup returned no result."
                )

            latencies.append(elapsed_ms)

        statistics = summarize_latencies(
            latencies
        )

        print()
        print(
            "## Indexed/filtered lookup results"
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

        import json

        output = {
            "database": "cognodb",
            "workload": "indexed_filtered_lookup",
            "query": QUERY.strip(),
            "warmup_iterations": WARMUP_ITERATIONS,
            "measured_iterations": MEASURED_ITERATIONS,
            "statistics": statistics,
            "index": "User.bucket",
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
            f"Results written to: {RESULT_FILE}"
        )

    finally:

        connection.close()


if __name__ == "__main__":
    main()