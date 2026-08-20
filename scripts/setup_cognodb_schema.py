from src.connections.cognodb import CognoDBConnection


def main():
    connection = CognoDBConnection()

    try:
        connection.verify_connectivity()

        query = """
        CREATE CONSTRAINT user_id_unique IF NOT EXISTS
        FOR (user:User)
        REQUIRE user.id IS UNIQUE
        """

        connection.execute_query(query)

        print("CognoDB schema setup: SUCCESS")
        print("Constraint/index created for User.id")

    finally:
        connection.close()


if __name__ == "__main__":
    main()