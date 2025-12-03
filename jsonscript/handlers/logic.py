from typing import List, Any
from jsonscript.environment import Environment
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc


class LogicHandler(BaseHandler):
    """
    Handles boolean logic and comparisons.
    """

    def can_handle(self, command: str) -> bool:
        return command in {
            "==", 
            "!=", 
            "<", 
            ">", 
            "<=", 
            ">="
        }

    def handle(self, command: str, args: List[Any], env: Environment, evaluator: EvaluatorFunc) -> Any:
        # Helper pour évaluer les arguments gauche (0) et droite (1)
        left = evaluator(args[0], env)
        right = evaluator(args[1], env)

        if command == "==": 
            return left == right
        
        if command == "!=": 
            return left != right
        
        if command == "<":  
            return left < right
        
        if command == ">":  
            return left > right
        
        if command == "<=": 
            return left <= right
        
        if command == ">=": 
            return left >= right

        raise ValueError(f"LogicHandler cannot handle: {command}")
    