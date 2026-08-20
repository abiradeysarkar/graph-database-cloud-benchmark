from neo4j import GraphDatabase

from src.config import (
    COGNODB_URI,
    COGNODB_USERNAME,
    COGNODB_PASSWORD,
    validate_cognodb_configuration,
)


class CognoDBConnection:
    """Manages the Neo4j driver connection to CognoDB Cloud."""

    def __init__(self):
        validate_cognodb_configuration()

        self.driver = GraphDatabase.driver(
            COGNODB_URI,
            auth=(
                COGNODB_USERNAME,
                COGNODB_PASSWORD,
            ),
        )

    def verify_connectivity(self):
        """Verify that the CognoDB instance is reachable."""

        self.driver.verify_connectivity()

    def execute_query(self, query, parameters=None):
        """Execute a Cypher query and return result records."""

        with self.driver.session() as session:
            result = session.run(
                query,
                parameters or {},
            )

            return result.data()

    def close(self):
        """Close the database driver."""

        self.driver.close()