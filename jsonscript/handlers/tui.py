import os
import getpass
from typing import List, Any
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc
from jsonscript.environment import Environment


class TUIHandler(BaseHandler):
    COLORS = {
        "red": "\033[91m", 
        "green": "\033[92m", 
        "yellow": "\033[93m",
        "blue": "\033[94m", 
        "bold": "\033[1m", 
        "reset": "\033[0m"
    }

    def can_handle(self, command):
        return command in {
            "print_color",
            "clear_screen",
            "input_password"
        }
    
    def handle(self, command: str, args: List[Any], env: Environment, evaluator: EvaluatorFunc) -> Any:
        if command == "print_color":
            text = str(evaluator(args[0], env))
            color_name = str(evaluator(args[1], env)).lower()
            code = self.COLORS.get(color_name, "")
            print(f"{code}{text}{self.COLORS['reset']}")
            return None

        if command == "clear_screen":
            os.system('cls' if os.name == 'nt' else 'clear')
            return None

        if command == "input_password":
            prompt = str(evaluator(args[0], env))
            return getpass.getpass(prompt)
        