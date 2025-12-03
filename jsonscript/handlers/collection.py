from typing import List, Any
from jsonscript.environment import Environment
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc


class CollectionHandler(BaseHandler):
    """
    Handles List and Dictionary reading operations.
    """

    def can_handle(self, command: str) -> bool:
        return command in {
            "len", 
            "at"
        }

    def handle(self, command: str, args: List[Any], env: Environment, evaluator: EvaluatorFunc) -> Any:
        
        target = evaluator(args[0], env)

        if command == "len":
            if not hasattr(target, '__len__'):
                raise ValueError("Object has no length.")
            return len(target)

        if command == "at":
            # args[0] = target, args[1] = key/index
            key_or_index = evaluator(args[1], env)

            try:
                if isinstance(target, list):
                    return target[int(key_or_index)]
                elif isinstance(target, dict):
                    return target[key_or_index]
                elif isinstance(target, str):
                    return target[int(key_or_index)]
                else:
                    raise ValueError(f"Cannot use 'at' on type {type(target).__name__}")
            except (IndexError, KeyError):
                raise ValueError(f"Key/Index '{key_or_index}' not found in target.")

        raise ValueError(f"CollectionHandler cannot handle: {command}")
    