from src.connections.cognodb import CognoDBConnection


def main():
    """Verify connectivity and execute a basic Cypher query."""

    connection = CognoDBConnection()

    try:
        connection.verify_connectivity()

        result = connection.execute_query(
            "RETURN 1 AS connectivity_check"
        )

        print("CognoDB Cloud connectivity verification: SUCCESS")
        print(f"Cypher query result: {result[0]['connectivity_check']}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()