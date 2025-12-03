from typing import Any


class ReturnValue(Exception):
    """Special exception to interrupt execution and return a value."""
    def __init__(self, value: Any):
        self.value = value
        

class BreakLoop(Exception):
    """Special exception to break out of a loop."""
    pass


class ContinueLoop(Exception):
    """Special exception to skip to the next loop iteration."""
    pass
