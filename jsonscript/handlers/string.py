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
            "parse_json",
            "to_json",
            "trim",
            "substring",
            "contains",
            "index_of",
            "starts_with",
            "ends_with"
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
        
        if command == "to_json":
            # ["to_json", variable]
            target = evaluator(args[0], env)
            try:
                # separators=(',', ':') compacte le JSON (enlève les espaces inutiles)
                return json.dumps(target, separators=(',', ':'))
            except TypeError as e:
                raise ValueError(f"Cannot serialize to JSON: {e}")

        if command == "trim":
            return eval_str(0).strip()

        if command == "contains":
            return eval_str(1) in eval_str(0)

        if command == "starts_with":
            return eval_str(0).startswith(eval_str(1))

        if command == "ends_with":
            return eval_str(0).endswith(eval_str(1))

        if command == "index_of":
            return eval_str(0).find(eval_str(1))

        if command == "substring":
            text = eval_str(0)
            start = int(evaluator(args[1], env))
            end = int(evaluator(args[2], env))
            return text[start:end]
        
        raise ValueError(f"StringHandler cannot handle: {command}")
    