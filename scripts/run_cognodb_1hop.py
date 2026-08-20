import csv
import json
import random
import time
from pathlib import Path

from src.benchmark.statistics import summarize_latencies
from src.connections.cognodb import CognoDBConnection


DATASET_FILE = Path(
    "data/processed/pokec_benchmark_edges.csv"
)

RESULTS_DIRECTORY = Path("results/cognodb")

WARMUP_ITERATIONS = 20
MEASURED_ITERATIONS = 100

RANDOM_SEED = 20260820


QUERY = """
MATCH (u:User {id: $user_id})-[:FOLLOWS]->(v:User)
RETURN v.id AS user_id
"""


def load_start_nodes():
    """Return valid source nodes from the benchmark dataset."""

    nodes = set()

    with DATASET_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            nodes.add(int(row["source_id"]))

    return sorted(nodes)


def choose_start_nodes(nodes, count):
    """Select deterministic start nodes for the benchmark."""

    if len(nodes) < count:
        raise ValueError(
            f"Only {len(nodes)} valid start nodes available."
        )

    random_generator = random.Random(RANDOM_SEED)

    return random_generator.sample(
        nodes,
        count,
    )


def execute_query(connection, user_id):
    """Execute one 1-hop traversal and measure latency."""

    start = time.perf_counter()

    result = connection.execute_query(
        QUERY,
        {"user_id": user_id},
    )

    elapsed_ms = (
        time.perf_counter() - start
    ) * 1000

    return elapsed_ms, result


def main():

    nodes = load_start_nodes()

    total_iterations = (
        WARMUP_ITERATIONS
        + MEASURED_ITERATIONS
    )

    start_nodes = choose_start_nodes(
        nodes,
        total_iterations,
    )

    connection = CognoDBConnection()

    try:

        connection.verify_connectivity()

        print(
            "CognoDB 1-hop traversal benchmark"
        )
        print(
            "---------------------------------"
        )
        print(
            f"Valid start nodes : {len(nodes):,}"
        )
        print(
            f"Warm-up iterations: "
            f"{WARMUP_ITERATIONS}"
        )
        print(
            f"Measured iterations: "
            f"{MEASURED_ITERATIONS}"
        )

        # Warm-up phase

        print()
        print("Running warm-up...")

        for user_id in start_nodes[
            :WARMUP_ITERATIONS
        ]:

            execute_query(
                connection,
                user_id,
            )

        # Measurement phase

        print(
            "Running measured queries..."
        )

        latencies = []

        for user_id in start_nodes[
            WARMUP_ITERATIONS:
        ]:

            latency_ms, _ = execute_query(
                connection,
                user_id,
            )

            latencies.append(
                latency_ms
            )

        statistics = summarize_latencies(
            latencies
        )

        print()
        print(
            "1-hop traversal results"
        )
        print(
            "-----------------------"
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

        RESULTS_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        result = {
            "database": "CognoDB",
            "workload": "1-hop traversal",
            "warmup_iterations": (
                WARMUP_ITERATIONS
            ),
            "measured_iterations": (
                MEASURED_ITERATIONS
            ),
            "statistics": statistics,
        }

        result_file = (
            RESULTS_DIRECTORY
            / "1hop.json"
        )

        with result_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                result,
                file,
                indent=2,
            )

        print()
        print(
            f"Results written to: {result_file}"
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()