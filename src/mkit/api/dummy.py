"""Dummy API module."""

class Dummy:
    """A dummy class for demonstration purposes.

    This class provides basic utility methods for demonstration and testing.
    """

    @staticmethod
    def sum(a: int, b: int) -> int:  # pylint: disable=no-self-argument
        """Add two integers and return the result.

        Args:
            a: The first integer to add.
            b: The second integer to add.

        Returns:
            The sum of a and b.
        """
        return a + b

    @staticmethod
    def rest(a: int, b: int) -> int:  # pylint: disable=no-self-argument
        """Rest two integers and return the result.

        Args:
            a: The first integer to add.
            b: The second integer to add.

        Returns:
            The rest of a and b.
        """
        return a - b

    @staticmethod
    def multiply(a: int, b: int) -> int:  # pylint: disable=no-self-argument
        """multiply two integers and return the result.

        Args:
            a: The first integer to add.
            b: The second integer to add.

        Returns:
            The multiply of a and b.
        """
        return a * b
