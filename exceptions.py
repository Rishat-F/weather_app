"""Application exceptions."""


class CantGetGpsCoordinates(Exception):
    """Program can't get current GPS coordinates."""


class NoSuchCommand(Exception):
    """There is no such command in system."""


class CommandRunsTooLong(Exception):
    """Command runs too long."""
