import json
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from src.connections.cognodb import CognoDBConnection


CONCURRENCY = 1
DURATION_SECONDS = 60

READ_RATIO = 0.80
WRITE_RATIO = 0.20

RESULT_FILE = Path(
    "results/cognodb/mixed_workload_1_client.json"
)


READ_QUERY = """
MATCH (u:User {id: $user_id})-[:FOLLOWS]->(f)
RETURN count(f) AS following_count
"""


WRITE_QUERY = """
MATCH (source:User {id: $source_id})
MATCH (target:User {id: $target_id})
MERGE (source)-[:BENCHMARK_WRITE]->(target)
"""


CLEANUP_QUERY = """
MATCH ()-[r:BENCHMARK_WRITE]->()
DELETE r
"""


def execute_worker(worker_id, stop_time):

    connection = CognoDBConnection()

    reads = 0
    writes = 0
    errors = 0

    latencies = []

    try:

        connection.verify_connectivity()

        while time.perf_counter() < stop_time:

            operation_value = random.random()

            source_id = random.randint(
                1,
                297688,
            )

            target_id = random.randint(
                1,
                297688,
            )

            start = time.perf_counter()

            try:

                if operation_value < READ_RATIO:

                    connection.execute_query(
                        READ_QUERY,
                        {
                            "user_id": source_id
                        },
                    )

                    reads += 1

                else:

                    connection.execute_query(
                        WRITE_QUERY,
                        {
                            "source_id": source_id,
                            "target_id": target_id,
                        },
                    )

                    writes += 1

                elapsed_ms = (
                    time.perf_counter() - start
                ) * 1000

                latencies.append(
                    elapsed_ms
                )

            except Exception:

                errors += 1

    finally:

        connection.close()

    return {
        "worker_id": worker_id,
        "reads": reads,
        "writes": writes,
        "errors": errors,
        "latencies": latencies,
    }


def main():

    print()
    print(
        "## CognoDB mixed read/write benchmark"
    )

    print(
        f"Concurrency       : {CONCURRENCY}"
    )

    print(
        f"Duration           : "
        f"{DURATION_SECONDS} seconds"
    )

    print(
        f"Read ratio         : "
        f"{READ_RATIO * 100:.0f}%"
    )

    print(
        f"Write ratio        : "
        f"{WRITE_RATIO * 100:.0f}%"
    )

    connection = CognoDBConnection()

    try:

        connection.verify_connectivity()

        print()
        print("Connectivity: SUCCESS")
        print("Starting workload...")

    finally:

        connection.close()

    start_time = time.perf_counter()

    stop_time = (
        start_time
        + DURATION_SECONDS
    )

    worker_results = []

    with ThreadPoolExecutor(
        max_workers=CONCURRENCY
    ) as executor:

        futures = [
            executor.submit(
                execute_worker,
                worker_id,
                stop_time,
            )
            for worker_id in range(
                CONCURRENCY
            )
        ]

        for future in as_completed(
            futures
        ):

            worker_results.append(
                future.result()
            )

    elapsed_seconds = (
        time.perf_counter()
        - start_time
    )

    total_reads = sum(
        result["reads"]
        for result in worker_results
    )

    total_writes = sum(
        result["writes"]
        for result in worker_results
    )

    total_errors = sum(
        result["errors"]
        for result in worker_results
    )

    all_latencies = []

    for result in worker_results:

        all_latencies.extend(
            result["latencies"]
        )

    total_operations = (
        total_reads
        + total_writes
    )

    throughput = (
        total_operations
        / elapsed_seconds
    )

    sorted_latencies = sorted(
        all_latencies
    )

    def percentile(values, p):

        if not values:
            return 0

        index = (
            (len(values) - 1)
            * p
            / 100
        )

        lower = int(index)

        upper = min(
            lower + 1,
            len(values) - 1,
        )

        fraction = (
            index - lower
        )

        return (
            values[lower]
            + (
                values[upper]
                - values[lower]
            )
            * fraction
        )

    p50 = percentile(
        sorted_latencies,
        50,
    )

    p95 = percentile(
        sorted_latencies,
        95,
    )

    mean = (
        statistics.mean(
            all_latencies
        )
        if all_latencies
        else 0
    )

    # Remove temporary benchmark relationships.

    cleanup_connection = (
        CognoDBConnection()
    )

    try:

        cleanup_connection.verify_connectivity()

        cleanup_connection.execute_query(
            CLEANUP_QUERY
        )

    finally:

        cleanup_connection.close()

    print()
    print(
        "## Mixed workload results"
    )

    print(
        f"Elapsed time       : "
        f"{elapsed_seconds:.3f} seconds"
    )

    print(
        f"Total operations   : "
        f"{total_operations:,}"
    )

    print(
        f"Reads              : "
        f"{total_reads:,}"
    )

    print(
        f"Writes             : "
        f"{total_writes:,}"
    )

    print(
        f"Errors             : "
        f"{total_errors:,}"
    )

    print(
        f"Throughput         : "
        f"{throughput:.2f} ops/sec"
    )

    print(
        f"p50 latency        : "
        f"{p50:.3f} ms"
    )

    print(
        f"p95 latency        : "
        f"{p95:.3f} ms"
    )

    print(
        f"Mean latency       : "
        f"{mean:.3f} ms"
    )

    RESULT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "database": "cognodb",
        "workload": "mixed_read_write",
        "concurrency": CONCURRENCY,
        "duration_seconds": elapsed_seconds,
        "read_ratio": READ_RATIO,
        "write_ratio": WRITE_RATIO,
        "total_operations": total_operations,
        "reads": total_reads,
        "writes": total_writes,
        "errors": total_errors,
        "operations_per_second": throughput,
        "p50_ms": p50,
        "p95_ms": p95,
        "mean_ms": mean,
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


if __name__ == "__main__":
    main()