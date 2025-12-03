from typing import Any


class ReturnValue(Exception):
    """Special exception to interrupt execution and return a value."""
    def __init__(self, value: Any):
        self.value = value
        