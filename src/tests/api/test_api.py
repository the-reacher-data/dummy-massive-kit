"""Tests for the dummy API module."""

from mkit.api.dummy import Dummy


class TestApi:
    """Test cases for the Dummy API class."""

    def test_sum_positive_integers(self) -> None:
        """Test the sum static method with positive integers."""
        expected_result = 3
        assert Dummy.sum(1, 2) == expected_result

    def test_sum_negative_integers(self) -> None:
        """Test the sum static method with negative integers."""
        expected_result = -3
        assert Dummy.sum(-1, -2) == expected_result

    def test_sum_large_numbers(self) -> None:
        """Test the sum static method with large integers to verify no overflow."""
        large_sum = 999999999999999 + 1
        assert Dummy.sum(999999999999999, 1) == large_sum
