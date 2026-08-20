import os

from dotenv import load_dotenv


load_dotenv()


COGNODB_URI = os.getenv("COGNODB_URI")
COGNODB_USERNAME = os.getenv("COGNODB_USERNAME")
COGNODB_PASSWORD = os.getenv("COGNODB_PASSWORD")


def validate_cognodb_configuration():
    """Validate that all required CognoDB connection settings are present."""

    required_settings = {
        "COGNODB_URI": COGNODB_URI,
        "COGNODB_USERNAME": COGNODB_USERNAME,
        "COGNODB_PASSWORD": COGNODB_PASSWORD,
    }

    missing_settings = [
        name for name, value in required_settings.items()
        if not value
    ]

    if missing_settings:
        raise ValueError(
            "Missing required configuration: "
            + ", ".join(missing_settings)
        )