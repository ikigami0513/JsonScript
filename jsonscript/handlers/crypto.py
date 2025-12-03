import hashlib
import base64
from typing import List, Any
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc


class CryptoEncodingHandler(BaseHandler):
    """
    Handles Cryptography (Hash) and Encoding (Base64).
    """

    def can_handle(self, command: str) -> bool:
        return command in {
            "hash_md5", 
            "hash_sha256", 
            "base64_encode", 
            "base64_decode"
        }
    
    def handle(self, command: str, args: List[Any], env: Any, evaluator: EvaluatorFunc) -> Any:
        
        def eval_str(i): return str(evaluator(args[i], env))

        if command == "hash_md5":
            data = eval_str(0).encode('utf-8')
            return hashlib.md5(data).hexdigest()

        if command == "hash_sha256":
            data = eval_str(0).encode('utf-8')
            return hashlib.sha256(data).hexdigest()

        if command == "base64_encode":
            data = eval_str(0).encode('utf-8')
            return base64.b64encode(data).decode('utf-8')

        if command == "base64_decode":
            data = eval_str(0).encode('utf-8')
            return base64.b64decode(data).decode('utf-8')

        raise ValueError(f"CryptoEncodingHandler cannot handle: {command}")