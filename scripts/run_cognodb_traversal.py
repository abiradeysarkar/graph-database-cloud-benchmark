import argparse
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


QUERIES = {
    1: """
        MATCH (u:User {id: $user_id})
              -[:FOLLOWS]->
              (v:User)
        RETURN count(v) AS result_count
    """,

    2: """
        MATCH (u:User {id: $user_id})
              -[:FOLLOWS]->
              (v:User)
              -[:FOLLOWS]->
              (w:User)
        RETURN count(w) AS result_count
    """,

    3: """
        MATCH (u:User {id: $user_id})
              -[:FOLLOWS]->
              (v:User)
              -[:FOLLOWS]->
              (w:User)
              -[:FOLLOWS]->
              (x:User)
        RETURN count(x) AS result_count
    """,
}


def load_start_nodes():
    """Load valid source nodes from the canonical dataset."""

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
    """Choose deterministic start nodes."""

    if len(nodes) < count:
        raise ValueError(
            f"Only {len(nodes)} start nodes available."
        )

    generator = random.Random(RANDOM_SEED)

    return generator.sample(
        nodes,
        count,
    )


def execute_query(connection, query, user_id):
    """Execute one traversal and measure client-observed latency."""

    start = time.perf_counter()

    result = connection.execute_query(
        query,
        {"user_id": user_id},
    )

    elapsed_ms = (
        time.perf_counter() - start
    ) * 1000

    return elapsed_ms, result


def run_benchmark(hops):

    if hops not in QUERIES:
        raise ValueError(
            "Hops must be 1, 2, or 3."
        )

    nodes = load_start_nodes()

    total_iterations = (
        WARMUP_ITERATIONS
        + MEASURED_ITERATIONS
    )

    start_nodes = choose_start_nodes(
        nodes,
        total_iterations,
    )

    query = QUERIES[hops]

    connection = CognoDBConnection()

    try:

        connection.verify_connectivity()

        print()
        print(
            f"CognoDB {hops}-hop traversal benchmark"
        )
        print(
            "-------------------------------------"
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

        # -------------------------
        # Warm-up
        # -------------------------

        print()
        print("Running warm-up...")

        for user_id in start_nodes[
            :WARMUP_ITERATIONS
        ]:

            execute_query(
                connection,
                query,
                user_id,
            )

        # -------------------------
        # Measurement
        # -------------------------

        print(
            "Running measured queries..."
        )

        latencies = []

        for user_id in start_nodes[
            WARMUP_ITERATIONS:
        ]:

            latency_ms, _ = execute_query(
                connection,
                query,
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
            f"{hops}-hop traversal results"
        )
        print(
            "---------------------------"
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

        # -------------------------
        # Save results
        # -------------------------

        RESULTS_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        result = {
            "database": "CognoDB",
            "workload": f"{hops}-hop traversal",
            "warmup_iterations": (
                WARMUP_ITERATIONS
            ),
            "measured_iterations": (
                MEASURED_ITERATIONS
            ),
            "random_seed": RANDOM_SEED,
            "statistics": statistics,
        }

        result_file = (
            RESULTS_DIRECTORY
            / f"{hops}hop.json"
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


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Run CognoDB traversal benchmark."
        )
    )

    parser.add_argument(
        "--hops",
        type=int,
        required=True,
        choices=[1, 2, 3],
        help="Traversal depth.",
    )

    args = parser.parse_args()

    run_benchmark(args.hops)


if __name__ == "__main__":
    main()