from typing import List, Any
from jsonscript.environment import Environment
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc
from jsonscript.exceptions import ReturnValue


class CoreHandler(BaseHandler):
    """
    Handles variable access, introspection, and function calls.
    """

    def can_handle(self, command: str) -> bool:
        return command in {
            "get", 
            "type", 
            "call"
        }

    def handle(self, command: str, args: List[Any], env: Environment, evaluator: EvaluatorFunc) -> Any:
        if command == "get":
            # args[0] is the variable name (string literal)
            if not args: raise ValueError("Invalid 'get' expression.")
            return env.get_variable(args[0])

        if command == "type":
            target = evaluator(args[0], env)
            return type(target).__name__

        if command == "call":
            # Local import
            from jsonscript.factory import InstructionFactory

            func_name = args[0]
            call_args = args[1:]
            
            # 1. Retrieve definition
            func_def = env.get_function(func_name)
            
            # 2. Resolve arguments (Evaluate them first)
            resolved_args = [evaluator(arg, env) for arg in call_args]

            # --- CAS 1 : FONCTION NATIVE PYTHON ---
            if func_def.get("type") == "native":
                python_func = func_def["ref"]
                try:
                    # On appelle directement la fonction Python avec les arguments résolus
                    return python_func(*resolved_args)
                except Exception as e:
                    raise RuntimeError(f"Error calling native function '{func_name}': {e}")

            # --- CAS 2 : FONCTION JSONSCRIPT (Legacy) ---
            # (Note : On adapte l'ancien code pour gérer le dictionnaire structurel)
            elif func_def.get("type") == "script" or "params" in func_def: 
                # "params" in func_def c'est pour la rétrocompatibilité si tu as une vieille version de l'env
                
                param_names = func_def["params"]
                body = func_def["body"]

                if len(resolved_args) != len(param_names):
                    raise ValueError(f"Function '{func_name}' expects {len(param_names)} args, got {len(resolved_args)}.")

                env.enter_scope()
                for name, val in zip(param_names, resolved_args):
                    env.set_variable(name, val)

                return_val = None
                try:
                    for raw_inst in body:
                        InstructionFactory.build(raw_inst).execute(env)
                except ReturnValue as ret:
                    return_val = ret.value
                finally:
                    env.exit_scope()
                
                return return_val
            
            else:
                raise ValueError(f"Unknown function type for '{func_name}'")
    