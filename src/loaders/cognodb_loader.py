import csv
import time
from pathlib import Path

from src.connections.cognodb import CognoDBConnection


DATASET_FILE = Path(
    "data/processed/pokec_benchmark_edges.csv"
)

BATCH_SIZE = 1000


def load_batch(tx, edges):
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


def load_dataset(connection):
    """Load the canonical Pokec dataset into CognoDB."""

    if not DATASET_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_FILE}"
        )

    total_relationships = 0
    total_batches = 0

    start_time = time.perf_counter()

    with DATASET_FILE.open(
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
                        "source_id": int(row["source_id"]),
                        "target_id": int(row["target_id"]),
                    }
                )

                if len(batch) >= BATCH_SIZE:

                    session.execute_write(
                        load_batch,
                        batch,
                    )

                    total_relationships += len(batch)
                    total_batches += 1
                    batch = []

            if batch:
                session.execute_write(
                    load_batch,
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
    print("CognoDB dataset ingestion")
    print("-------------------------")
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
        "relationships_per_second": relationships_per_second,
    }


def main():
    connection = CognoDBConnection()

    try:
        connection.verify_connectivity()

        print("CognoDB Cloud connectivity: SUCCESS")
        print("Starting dataset ingestion...")

        load_dataset(connection)

    finally:
        connection.close()


if __name__ == "__main__":
    main()