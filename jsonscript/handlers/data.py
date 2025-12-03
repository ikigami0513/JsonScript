import csv
from typing import List, Any
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc
from jsonscript.environment import Environment


class DataHandler(BaseHandler):
    def can_handle(self, command: str) -> bool:
        return command in {
            "read_csv",
            "write_csv"
        }
    
    def handle(self, command: str, args: List[Any], env: Environment, evaluator: EvaluatorFunc) -> Any:
        path = str(evaluator(args[0], env))

        if command == "read_csv":
            try:
                with open(path, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    return list(reader) # Convertit en liste de dicts
            except Exception as e:
                raise RuntimeError(f"CSV Read Error: {e}")

        if command == "write_csv":
            data = evaluator(args[1], env)
            if not isinstance(data, list) or not data:
                return False
            
            try:
                with open(path, mode='w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                return True
            except Exception as e:
                raise RuntimeError(f"CSV Write Error: {e}")