"""Tests for the dummy API module."""

from dummy_massivekit.api.dummy import Dummy


class TestApi:
    """Test cases for the Dummy API class."""

    def test_sum(self) -> None:
        """Test the sum static method with positive integers."""
        expected_result = 3
        assert Dummy.sum(1, 2) == expected_result

    def test_sum_negative_numbers(self) -> None:
        """Test the sum static method with negative integers."""
        expected_result = -3
        assert Dummy.sum(-1, -2) == expected_result
