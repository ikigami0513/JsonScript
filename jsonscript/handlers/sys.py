import os
import platform
import subprocess
from typing import List, Any
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc


class SysHandler(BaseHandler):
    """
    Handles System interactions and Shell commands.
    """

    def can_handle(self, command: str) -> bool:
        return command in {
            "exec", 
            "os_name", 
            "cwd", 
            "env"
        }

    def handle(self, command: str, args: List[Any], env: Any, evaluator: EvaluatorFunc) -> Any:
        # ["exec", "echo hello"] -> Retourne la sortie standard (stdout)
        if command == "exec":
            cmd_str = str(evaluator(args[0], env))
            try:
                # On utilise subprocess pour capturer la sortie
                result = subprocess.run(
                    cmd_str, 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                # On peut choisir de retourner juste le stdout, 
                # ou un dict {"stdout": ..., "stderr": ..., "code": ...}
                # Pour rester simple, retournons le stdout, sauf si erreur
                if result.returncode != 0:
                    raise OSError(f"Command failed (code {result.returncode}): {result.stderr.strip()}")
                return result.stdout.strip()
            except Exception as e:
                raise OSError(f"Exec error: {e}")

        # ["os_name"] -> "Windows", "Linux", "Darwin"
        if command == "os_name":
            return platform.system()

        # ["cwd"] -> Current Working Directory
        if command == "cwd":
            return os.getcwd()

        # ["env", "PATH"] -> Valeur de la variable d'environnement
        if command == "env":
            var_name = str(evaluator(args[0], env))
            return os.environ.get(var_name, "")

        raise ValueError(f"SysHandler cannot handle: {command}")
    