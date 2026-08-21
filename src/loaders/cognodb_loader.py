import csv
import time
from pathlib import Path

from src.connections.cognodb import CognoDBConnection


USERS_FILE = Path(
    "data/processed/pokec_benchmark_users.csv"
)

EDGES_FILE = Path(
    "data/processed/pokec_benchmark_edges.csv"
)

BATCH_SIZE = 1000


def load_user_batch(tx, users):
    """Insert/update one batch of canonical users."""

    query = """
    UNWIND $users AS user

    MERGE (u:User {id: user.user_id})

    SET u.bucket = user.bucket
    """

    tx.run(
        query,
        users=users,
    )


def load_users(connection):
    """Load canonical users and their bucket property."""

    if not USERS_FILE.exists():
        raise FileNotFoundError(
            f"User dataset not found: {USERS_FILE}"
        )

    total_users = 0
    total_batches = 0

    start_time = time.perf_counter()

    with USERS_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)
        batch = []

        with connection.driver.session() as session:

            for row in reader:

                batch.append(
                    {
                        "user_id": int(row["user_id"]),
                        "bucket": int(row["bucket"]),
                    }
                )

                if len(batch) >= BATCH_SIZE:

                    session.execute_write(
                        load_user_batch,
                        batch,
                    )

                    total_users += len(batch)
                    total_batches += 1
                    batch = []

            if batch:

                session.execute_write(
                    load_user_batch,
                    batch,
                )

                total_users += len(batch)
                total_batches += 1

    elapsed_seconds = (
        time.perf_counter() - start_time
    )

    users_per_second = (
        total_users / elapsed_seconds
        if elapsed_seconds > 0
        else 0
    )

    print()
    print("CognoDB user ingestion")
    print("----------------------")
    print(
        f"Users loaded          : "
        f"{total_users:,}"
    )
    print(
        f"Batch size            : "
        f"{BATCH_SIZE:,}"
    )
    print(
        f"Total batches         : "
        f"{total_batches:,}"
    )
    print(
        f"Wall-clock time       : "
        f"{elapsed_seconds:.3f} seconds"
    )
    print(
        f"Users/sec             : "
        f"{users_per_second:,.2f}"
    )

    return {
        "users": total_users,
        "batches": total_batches,
        "elapsed_seconds": elapsed_seconds,
        "users_per_second": users_per_second,
    }


def load_edge_batch(tx, edges):
    """Insert one batch of Pokec relationships."""

    query = """
    UNWIND $edges AS edge

    MERGE (source:User {id: edge.source_id})
    MERGE (target:User {id: edge.target_id})

    MERGE (source)-[:FOLLOWS]->(target)
    """

    tx.run(
        query,
        edges=edges,
    )


def load_edges(connection):
    """Load the canonical Pokec relationships."""

    if not EDGES_FILE.exists():
        raise FileNotFoundError(
            f"Edge dataset not found: {EDGES_FILE}"
        )

    total_relationships = 0
    total_batches = 0

    start_time = time.perf_counter()

    with EDGES_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)
        batch = []

        with connection.driver.session() as session:

            for row in reader:

                batch.append(
                    {
                        "source_id": int(
                            row["source_id"]
                        ),
                        "target_id": int(
                            row["target_id"]
                        ),
                    }
                )

                if len(batch) >= BATCH_SIZE:

                    session.execute_write(
                        load_edge_batch,
                        batch,
                    )

                    total_relationships += len(batch)
                    total_batches += 1
                    batch = []

            if batch:

                session.execute_write(
                    load_edge_batch,
                    batch,
                )

                total_relationships += len(batch)
                total_batches += 1

    elapsed_seconds = (
        time.perf_counter() - start_time
    )

    relationships_per_second = (
        total_relationships / elapsed_seconds
        if elapsed_seconds > 0
        else 0
    )

    print()
    print("CognoDB relationship ingestion")
    print("--------------------------------")
    print(
        f"Relationships loaded : "
        f"{total_relationships:,}"
    )
    print(
        f"Batch size            : "
        f"{BATCH_SIZE:,}"
    )
    print(
        f"Total batches         : "
        f"{total_batches:,}"
    )
    print(
        f"Wall-clock time       : "
        f"{elapsed_seconds:.3f} seconds"
    )
    print(
        f"Relationships/sec     : "
        f"{relationships_per_second:,.2f}"
    )

    return {
        "relationships": total_relationships,
        "batches": total_batches,
        "elapsed_seconds": elapsed_seconds,
        "relationships_per_second": (
            relationships_per_second
        ),
    }


def load_dataset(connection):
    """Load canonical users followed by relationships."""

    load_users(connection)

    load_edges(connection)


def main():

    connection = CognoDBConnection()

    try:

        connection.verify_connectivity()

        print(
            "CognoDB Cloud connectivity: SUCCESS"
        )

        print(
            "Starting dataset ingestion..."
        )

        load_dataset(connection)

    finally:

        connection.close()


if __name__ == "__main__":
    main()