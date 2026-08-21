import csv
from pathlib import Path


USERS_FILE = Path(
    "data/processed/pokec_benchmark_users.csv"
)


def main():

    users = set()
    invalid_buckets = 0
    duplicate_users = 0

    with USERS_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            user_id = int(row["user_id"])
            bucket = int(row["bucket"])

            if user_id in users:
                duplicate_users += 1

            users.add(user_id)

            if bucket != user_id % 100:
                invalid_buckets += 1

    print()
    print(
        "Pokec user dataset validation"
    )
    print(
        "-----------------------------"
    )
    print(
        f"Users             : {len(users):,}"
    )
    print(
        f"Duplicate users   : {duplicate_users}"
    )
    print(
        f"Invalid buckets   : {invalid_buckets}"
    )

    if duplicate_users != 0:
        raise RuntimeError(
            "Duplicate users detected."
        )

    if invalid_buckets != 0:
        raise RuntimeError(
            "Invalid bucket values detected."
        )

    print(
        "User dataset validation: PASS"
    )


if __name__ == "__main__":
    main()