from src.connections.cognodb import CognoDBConnection


def main():

    connection = CognoDBConnection()

    try:

        connection.verify_connectivity()

        user_id_constraint = """
        CREATE CONSTRAINT user_id_unique IF NOT EXISTS
        FOR (user:User)
        REQUIRE user.id IS UNIQUE
        """

        bucket_index = """
        CREATE INDEX user_bucket_index IF NOT EXISTS
        FOR (user:User)
        ON (user.bucket)
        """

        connection.execute_query(
            user_id_constraint
        )

        connection.execute_query(
            bucket_index
        )

        print(
            "CognoDB schema setup: SUCCESS"
        )

        print(
            "Unique constraint created for User.id"
        )

        print(
            "Index created for User.bucket"
        )

    finally:

        connection.close()


if __name__ == "__main__":
    main()