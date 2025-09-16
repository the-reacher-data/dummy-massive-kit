"""Tests for the dummy API module."""

from dummy_massivekit.api.dummy import Dummy


class TestApi:
    """Test cases for the Dummy API class."""

    def test_sum(self):
        """Test the sum static method with positive integers."""
        assert Dummy.sum(1, 2) == 3
