import csv
import hashlib
from pathlib import Path


DATASET_FILE = Path(
    "data/processed/pokec_benchmark_edges.csv"
)

EXPECTED_EDGE_COUNT = 200_000


def calculate_sha256(file_path):
    """Calculate SHA-256 checksum for a file."""

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


def validate_dataset():
    """Validate the canonical Pokec benchmark dataset."""

    if not DATASET_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_FILE}"
        )

    nodes = set()
    edges = set()

    duplicate_edges = 0
    self_loops = 0
    edge_count = 0

    with DATASET_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        expected_columns = {
            "source_id",
            "target_id",
        }

        if set(reader.fieldnames or []) != expected_columns:
            raise ValueError(
                f"Unexpected columns: {reader.fieldnames}"
            )

        for row in reader:
            source = int(row["source_id"])
            target = int(row["target_id"])

            edge = (source, target)

            edge_count += 1

            nodes.add(source)
            nodes.add(target)

            if source == target:
                self_loops += 1

            if edge in edges:
                duplicate_edges += 1
            else:
                edges.add(edge)

    checksum = calculate_sha256(DATASET_FILE)

    print("Pokec benchmark dataset validation")
    print("-----------------------------------")
    print(f"Relationships : {edge_count:,}")
    print(f"Unique nodes  : {len(nodes):,}")
    print(f"Duplicate edges: {duplicate_edges:,}")
    print(f"Self-loops    : {self_loops:,}")
    print(f"SHA-256       : {checksum}")

    if edge_count != EXPECTED_EDGE_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_EDGE_COUNT:,} relationships, "
            f"found {edge_count:,}"
        )

    if duplicate_edges > 0:
        raise ValueError(
            f"Dataset contains {duplicate_edges:,} duplicate edges."
        )

    print()
    print("Dataset validation: PASS")


if __name__ == "__main__":
    validate_dataset()