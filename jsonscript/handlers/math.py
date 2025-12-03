import math
import random
from typing import List, Any
from jsonscript.environment import Environment
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc


class MathHandler(BaseHandler):
    """
    Handles basic arithmetic (+, -, *, /) and advanced math functions (sqrt, random).
    """

    def can_handle(self, command: str) -> bool:
        return command in {
            "+", 
            "-", 
            "*", 
            "/", 
            "%", 
            "random", 
            "randint", 
            "sqrt", 
            "pow", 
            "abs", 
            "round", 
            "floor", 
            "ceil", 
            "PI"
        }

    def handle(self, command: str, args: List[Any], env: Environment, evaluator: EvaluatorFunc) -> Any:
        # Helper to evaluate arguments recursively
        def eval_arg(index):
            return evaluator(args[index], env)

        # --- Basic Arithmetic ---
        if command == "+": 
            val1 = eval_arg(0)
            val2 = eval_arg(1)
            
            # Si l'un des deux est une chaîne, on concatène (Style JavaScript)
            if isinstance(val1, str) or isinstance(val2, str):
                return str(val1) + str(val2)
            
            # Sinon, c'est une addition mathématique classique
            return val1 + val2
        
        if command == "-": 
            return eval_arg(0) - eval_arg(1)
        
        if command == "*": 
            return eval_arg(0) * eval_arg(1)
        
        if command == "/":
            denom = eval_arg(1)
            if denom == 0: 
                raise ValueError("Division by zero")
            return eval_arg(0) / denom
        
        if command == "%": 
            return eval_arg(0) % eval_arg(1)

        # --- Native Library ---
        if command == "random": 
            return random.random()
        
        if command == "randint": 
            return random.randint(int(eval_arg(0)), int(eval_arg(1)))
        
        if command == "sqrt": 
            return math.sqrt(eval_arg(0))
        
        if command == "pow": 
            return math.pow(eval_arg(0), eval_arg(1))
        
        if command == "abs": 
            return abs(eval_arg(0))
        
        if command == "floor": 
            return math.floor(eval_arg(0))
        
        if command == "ceil": 
            return math.ceil(eval_arg(0))
        
        if command == "PI": 
            return math.pi
        
        if command == "round":
            val = eval_arg(0)
            digits = int(eval_arg(1)) if len(args) > 1 else 0
            return round(val, digits)

        raise ValueError(f"MathHandler cannot handle: {command}")
    