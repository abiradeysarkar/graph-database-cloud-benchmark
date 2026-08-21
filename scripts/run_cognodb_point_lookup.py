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
MATCH (u:User {id: $user_id})
RETURN u.id AS user_id
"""


def load_user_ids():
    """Load unique user IDs from the canonical dataset."""

    user_ids = set()

    with DATASET_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            user_ids.add(int(row["source_id"]))
            user_ids.add(int(row["target_id"]))

    return sorted(user_ids)


def choose_user_ids(user_ids, count):
    """Choose deterministic user IDs."""

    if len(user_ids) < count:
        raise ValueError(
            f"Only {len(user_ids)} users available."
        )

    generator = random.Random(RANDOM_SEED)

    return generator.sample(
        user_ids,
        count,
    )


def execute_lookup(connection, user_id):
    """Execute one point lookup and measure latency."""

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

    user_ids = load_user_ids()

    total_iterations = (
        WARMUP_ITERATIONS
        + MEASURED_ITERATIONS
    )

    selected_user_ids = choose_user_ids(
        user_ids,
        total_iterations,
    )

    connection = CognoDBConnection()

    try:

        connection.verify_connectivity()

        print()
        print("CognoDB point lookup benchmark")
        print("------------------------------")
        print(
            f"Available users   : "
            f"{len(user_ids):,}"
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

        for user_id in selected_user_ids[
            :WARMUP_ITERATIONS
        ]:

            execute_lookup(
                connection,
                user_id,
            )

        print("Running measured queries...")

        latencies = []

        for user_id in selected_user_ids[
            WARMUP_ITERATIONS:
        ]:

            latency_ms, result = execute_lookup(
                connection,
                user_id,
            )

            if not result:
                raise RuntimeError(
                    f"User {user_id} was not found."
                )

            latencies.append(
                latency_ms
            )

        statistics = summarize_latencies(
            latencies
        )

        print()
        print("Point lookup results")
        print("--------------------")
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
            "workload": "point lookup",
            "property": "User.id",
            "index": (
                "UNIQUE constraint with "
                "backing index"
            ),
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
            / "point_lookup.json"
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