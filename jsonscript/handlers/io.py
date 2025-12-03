from typing import List, Any
from jsonscript.environment import Environment
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc


class IOHandler(BaseHandler):
    """
    Handles Input/Output operations that return values (like reading a file).
    """

    def can_handle(self, command: str) -> bool:
        return command == "read_file"

    def handle(self, command: str, args: List[Any], env: Environment, evaluator: EvaluatorFunc) -> Any:
        
        if command == "read_file":
            path = str(evaluator(args[0], env))
            # On ne met pas de try/catch ici pour laisser l'instruction "try" 
            # du langage gérer l'erreur FileNotFoundError si besoin.
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        raise ValueError(f"IOHandler cannot handle: {command}")
    