import os
import shutil
from typing import List, Any
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc


class FileSystemHandler(BaseHandler):
    """
    Handles Advanced Filesystem operations.
    """

    def can_handle(self, command: str) -> bool:
        return command in {
            "fs_exists", 
            "fs_list", 
            "fs_remove", 
            "fs_mkdir", 
            "fs_copy"
        }
    
    def handle(self, command: str, args: List[Any], env: Any, evaluator: EvaluatorFunc) -> Any:
        
        # Helper
        def eval_str(i): 
            return str(evaluator(args[i], env))

        if command == "fs_exists":
            return os.path.exists(eval_str(0))

        if command == "fs_list":
            path = eval_str(0)
            try:
                return os.listdir(path)
            except Exception as e:
                raise OSError(f"fs_list failed: {e}")

        if command == "fs_remove":
            path = eval_str(0)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                return True
            except:
                return False

        if command == "fs_mkdir":
            try:
                os.makedirs(eval_str(0), exist_ok=True)
                return True
            except: return False

        if command == "fs_copy":
            try:
                shutil.copy2(eval_str(0), eval_str(1))
                return True
            except: return False

        raise ValueError(f"FileSystemHandler cannot handle: {command}")
    