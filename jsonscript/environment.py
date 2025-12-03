from typing import Dict, Any, List


class Environment:
    def __init__(self):
        self._scopes: List[Dict[str, Any]] = [{}] 
        self._functions: Dict[str, Any] = {}
        self._classes: Dict[str, Any] = {}

    def enter_scope(self):
        self._scopes.append({})

    def exit_scope(self):
        if len(self._scopes) > 1:
            self._scopes.pop()
        else:
            raise RuntimeError("Cannot exit global scope.")

    def set_variable(self, name: str, value: Any) -> None:
        self._scopes[-1][name] = value

    def get_variable(self, name: str) -> Any:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        raise ValueError(f"Variable '{name}' is not defined.")

    def define_function(self, name: str, params: List[str], body: List[Any]) -> None:
        self._functions[name] = {
            "type": "script", 
            "params": params, 
            "body": body
        }

    def register_native_function(self, name: str, func_callable: Any) -> None:
        """
        Registers a pure Python function to be callable from JsonScript.
        """
        self._functions[name] = {
            "type": "native",
            "ref": func_callable
        }

    def get_function(self, name: str) -> Dict[str, Any]:
        func = self._functions.get(name)
        if func is None:
            raise ValueError(f"Function '{name}' is not defined.")
        return func
    
    def define_class(self, name: str, init_params: List[str], methods: Dict[str, Any]):
        self._classes[name] = {
            "params": init_params, # Pour le constructeur
            "methods": methods     # Dict de fonctions { "bark": {params, body} }
        }

    def get_class(self, name: str) -> Dict[str, Any]:
        cls = self._classes.get(name)
        if cls is None:
            raise ValueError(f"Class '{name}' is not defined.")
        return cls
