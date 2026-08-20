from src.connections.cognodb import CognoDBConnection


def main():
    connection = CognoDBConnection()

    try:
        connection.verify_connectivity()

        node_query = """
        MATCH (u:User)
        RETURN count(u) AS user_count
        """

        relationship_query = """
        MATCH ()-[r:FOLLOWS]->()
        RETURN count(r) AS relationship_count
        """

        node_result = connection.execute_query(
            node_query
        )

        relationship_result = connection.execute_query(
            relationship_query
        )

        user_count = node_result[0]["user_count"]
        relationship_count = relationship_result[0][
            "relationship_count"
        ]

        print("CognoDB dataset verification")
        print("----------------------------")
        print(f"Users          : {user_count:,}")
        print(
            f"FOLLOWS edges  : "
            f"{relationship_count:,}"
        )

        if user_count == 297_688:
            print("User count validation: PASS")
        else:
            print(
                "User count validation: FAIL "
                f"(expected 297,688)"
            )

        if relationship_count == 200_000:
            print(
                "Relationship count validation: PASS"
            )
        else:
            print(
                "Relationship count validation: FAIL "
                f"(expected 200,000)"
            )

    finally:
        connection.close()


if __name__ == "__main__":
    main()