import csv
import gzip
import hashlib
import random
import urllib.request
from pathlib import Path


DATASET_URL = (
    "https://snap.stanford.edu/data/"
    "soc-pokec-relationships.txt.gz"
)

RAW_DIRECTORY = Path("data/raw")
PROCESSED_DIRECTORY = Path("data/processed")

RAW_FILE = RAW_DIRECTORY / "soc-pokec-relationships.txt.gz"
PROCESSED_FILE = PROCESSED_DIRECTORY / "pokec_benchmark_edges.csv"
METADATA_FILE = PROCESSED_DIRECTORY / "pokec_benchmark_metadata.txt"

TARGET_EDGE_COUNT = 200_000
RANDOM_SEED = 20260820


def download_dataset():
    """Download the official SNAP Pokec relationship dataset."""

    RAW_DIRECTORY.mkdir(parents=True, exist_ok=True)

    if RAW_FILE.exists():
        print(f"Dataset already exists: {RAW_FILE}")
        return

    print("Downloading SNAP Pokec relationship dataset...")
    print(f"Source: {DATASET_URL}")

    urllib.request.urlretrieve(DATASET_URL, RAW_FILE)

    print(f"Downloaded: {RAW_FILE}")


def sample_edges():
    """Create a deterministic sample using reservoir sampling."""

    random_generator = random.Random(RANDOM_SEED)

    reservoir = []
    total_edges = 0

    print("Streaming source dataset...")

    with gzip.open(RAW_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            source, target = line.split()

            edge = (int(source), int(target))

            total_edges += 1

            if len(reservoir) < TARGET_EDGE_COUNT:
                reservoir.append(edge)
                continue

            replacement_index = random_generator.randint(
                0,
                total_edges - 1,
            )

            if replacement_index < TARGET_EDGE_COUNT:
                reservoir[replacement_index] = edge

    print(
        f"Source relationships processed: "
        f"{total_edges:,}"
    )

    print(
        f"Benchmark relationships selected: "
        f"{len(reservoir):,}"
    )

    reservoir.sort()

    return reservoir


def write_processed_dataset(edges):
    """Write the canonical benchmark dataset."""

    PROCESSED_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    with PROCESSED_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "source_id",
                "target_id",
            ]
        )

        writer.writerows(edges)

    print(
        f"Benchmark dataset written: "
        f"{PROCESSED_FILE}"
    )


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


def write_metadata(edges, checksum):
    """Write benchmark dataset metadata."""

    nodes = set()

    for source, target in edges:
        nodes.add(source)
        nodes.add(target)

    with METADATA_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "Dataset: SNAP soc-Pokec\n"
        )

        file.write(
            f"Source URL: {DATASET_URL}\n"
        )

        file.write(
            "Graph type: Directed\n"
        )

        file.write(
            f"Benchmark relationships: {len(edges):,}\n"
        )

        file.write(
            f"Benchmark nodes: {len(nodes):,}\n"
        )

        file.write(
            f"Sampling method: Deterministic random sampling\n"
        )

        file.write(
            f"Random seed: {RANDOM_SEED}\n"
        )

        file.write(
            f"SHA-256: {checksum}\n"
        )

    print(f"Metadata written: {METADATA_FILE}")
    print(f"Benchmark nodes: {len(nodes):,}")
    print(f"Benchmark relationships: {len(edges):,}")
    print(f"SHA-256: {checksum}")


def main():
    """Prepare the canonical Pokec benchmark dataset."""

    download_dataset()

    selected_edges = sample_edges()

    write_processed_dataset(selected_edges)

    checksum = calculate_sha256(PROCESSED_FILE)

    write_metadata(
        selected_edges,
        checksum,
    )


if __name__ == "__main__":
    main()