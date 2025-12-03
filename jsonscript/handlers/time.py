import time
from datetime import datetime
from typing import List, Any
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc


class TimeHandler(BaseHandler):
    """
    Handles Time, Date and Sleep.
    """

    def can_handle(self, command: str) -> bool:
        return command in {
            "now", 
            "timestamp",
            "format_date"
        }

    def handle(self, command: str, args: List[Any], env: Any, evaluator: EvaluatorFunc) -> Any:
        # ["now"] -> "2023-10-27 10:00:00" (ISO format string)
        if command == "now":
            return str(datetime.now())

        # ["timestamp"] -> 1698393600.0 (Unix timestamp float)
        if command == "timestamp":
            return time.time()

        # ["format_date", timestamp, "%Y-%m-%d"]
        if command == "format_date":
            ts = float(evaluator(args[0], env))
            fmt = str(evaluator(args[1], env))
            return datetime.fromtimestamp(ts).strftime(fmt)

        raise ValueError(f"TimeHandler cannot handle: {command}")
    