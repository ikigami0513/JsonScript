import json
import urllib.request
import urllib.error
from typing import List, Any
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc


class HttpHandler(BaseHandler):
    """
    Handles HTTP Requests (GET, POST) using Python's standard library.
    """
    def can_handle(self, command: str) -> bool:
        return command in {
            "http_get", 
            "http_post"
        }

    def handle(self, command: str, args: List[Any], env: Any, evaluator: EvaluatorFunc) -> Any:
        
        # 1. Resolve URL
        url = str(evaluator(args[0], env))

        # --- HTTP GET ---
        if command == "http_get":
            # Syntax: ["http_get", "https://api.example.com"]
            try:
                # Basic GET request
                with urllib.request.urlopen(url) as response:
                    # Return the body as a string
                    return response.read().decode('utf-8')
            except urllib.error.URLError as e:
                raise RuntimeError(f"HTTP Request failed: {e}")

        # --- HTTP POST ---
        if command == "http_post":
            # Syntax: ["http_post", "url", {data_dict}]
            if len(args) < 2: raise ValueError("http_post requires a URL and a Data Dictionary.")
            
            data_payload = evaluator(args[1], env)
            
            # Convert the dictionary to JSON bytes
            json_bytes = json.dumps(data_payload).encode('utf-8')
            
            # Build request with headers
            req = urllib.request.Request(url, data=json_bytes)
            req.add_header('Content-Type', 'application/json')
            req.add_header('User-Agent', 'JsonScript/1.0')

            try:
                with urllib.request.urlopen(req) as response:
                    return response.read().decode('utf-8')
            except urllib.error.URLError as e:
                raise RuntimeError(f"HTTP POST failed: {e}")

        raise ValueError(f"HttpHandler cannot handle: {command}")
    