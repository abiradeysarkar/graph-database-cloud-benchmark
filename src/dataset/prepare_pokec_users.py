import csv
from pathlib import Path


EDGES_FILE = Path(
    "data/processed/pokec_benchmark_edges.csv"
)

USERS_FILE = Path(
    "data/processed/pokec_benchmark_users.csv"
)


def extract_users():

    users = set()

    with EDGES_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            users.add(int(row["source_id"]))
            users.add(int(row["target_id"]))

    return sorted(users)


def write_users(users):

    USERS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with USERS_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            ["user_id", "bucket"]
        )

        for user_id in users:

            writer.writerow(
                [
                    user_id,
                    user_id % 100,
                ]
            )


def main():

    if not EDGES_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {EDGES_FILE}"
        )

    print(
        "Preparing canonical Pokec user dataset..."
    )

    users = extract_users()

    print(
        f"Unique users: {len(users):,}"
    )

    write_users(users)

    print(
        f"User dataset written: {USERS_FILE}"
    )


if __name__ == "__main__":
    main()