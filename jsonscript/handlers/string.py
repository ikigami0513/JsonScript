import json
from typing import List, Any
from jsonscript.environment import Environment
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc


class StringHandler(BaseHandler):
    """
    Handles string manipulations.
    """

    def can_handle(self, command: str) -> bool:
        return command in {
            "concat", 
            "split", 
            "replace", 
            "upper", 
            "lower",
            "parse_json"
        }

    def handle(self, command: str, args: List[Any], env: Environment, evaluator: EvaluatorFunc) -> Any:
        
        # Helper: Evaluate and convert to string
        def eval_str(index):
            return str(evaluator(args[index], env))

        if command == "concat":
            # Evaluates all arguments and joins them
            return "".join([str(evaluator(arg, env)) for arg in args])
        
        if command == "split":
            return eval_str(0).split(eval_str(1))
        
        if command == "replace":
            return eval_str(0).replace(eval_str(1), eval_str(2))
        
        if command == "upper":
            return eval_str(0).upper()
            
        if command == "lower":
            return eval_str(0).lower()
        
        if command == "parse_json":
            # ["parse_json", "{ 'key': 'val' }"] -> Dict
            json_str = str(evaluator(args[0], env))
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON string: {e}")

        raise ValueError(f"StringHandler cannot handle: {command}")
    