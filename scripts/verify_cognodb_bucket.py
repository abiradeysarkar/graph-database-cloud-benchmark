from src.connections.cognodb import CognoDBConnection


def main():

    connection = CognoDBConnection()

    try:
        connection.verify_connectivity()

        query = """
        MATCH (u:User)
        RETURN
            count(u) AS total_users,
            count(u.bucket) AS users_with_bucket,
            count(DISTINCT u.bucket) AS distinct_buckets
        """

        result = connection.execute_query(query)[0]

        total_users = result["total_users"]
        users_with_bucket = result["users_with_bucket"]
        distinct_buckets = result["distinct_buckets"]

        print()
        print("CognoDB bucket property verification")
        print("-------------------------------------")
        print(f"Total users        : {total_users:,}")
        print(f"Users with bucket  : {users_with_bucket:,}")
        print(f"Distinct buckets   : {distinct_buckets}")

        if total_users != users_with_bucket:
            raise RuntimeError(
                "Not all users have the bucket property."
            )

        if distinct_buckets != 100:
            raise RuntimeError(
                f"Expected 100 buckets, found {distinct_buckets}."
            )

        print("Bucket validation: PASS")

    finally:
        connection.close()


if __name__ == "__main__":
    main()