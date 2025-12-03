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
            from jsonscript.factory import InstructionFactory

            func_name = args[0]
            call_args = args[1:]

            # 1. Retrieve definition
            func_def = env.get_function(func_name)
            param_names = func_def["params"]
            body = func_def["body"]

            # 2. Check arity
            if len(call_args) != len(param_names):
                raise ValueError(f"Function '{func_name}' expects {len(param_names)} args, got {len(call_args)}.")

            # 3. Resolve arguments
            resolved_args = [evaluator(arg, env) for arg in call_args]

            # 4. Scope management
            env.enter_scope()
            for name, val in zip(param_names, resolved_args):
                env.set_variable(name, val)

            # 5. Execution
            return_val = None
            try:
                for raw_inst in body:
                    InstructionFactory.build(raw_inst).execute(env)
            except ReturnValue as ret:
                return_val = ret.value
            finally:
                env.exit_scope()
            
            return return_val

        raise ValueError(f"CoreHandler cannot handle: {command}")
    