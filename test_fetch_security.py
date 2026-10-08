import pytest

from researchops.tools.fetch import validate_url


def test_localhost_blocked():

    with pytest.raises(ValueError):

        validate_url(
            "http://localhost:8000"
        )


def test_file_protocol_blocked():

    with pytest.raises(ValueError):

        validate_url(
            "file:///etc/passwd"
        )


def test_credentials_blocked():

    with pytest.raises(ValueError):

        validate_url(
            "https://user:password@example.com"
        )