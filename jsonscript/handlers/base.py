from abc import ABC, abstractmethod
from typing import List, Any, Callable
from jsonscript.environment import Environment


# Type alias for the evaluator function to avoid circular imports in type hinting
EvaluatorFunc = Callable[[Any, Any], Any]


class BaseHandler(ABC):
    """
    Abstract base class for all expression handlers.
    """
    
    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """Returns True if this handler supports the given command."""
        pass

    @abstractmethod
    def handle(self, command: str, args: List[Any], env: Environment, evaluator: EvaluatorFunc) -> Any:
        """
        Executes the logic.
        
        :param command: The operator/function name (e.g., "+", "split").
        :param args: The list of raw arguments (e.g., [["get", "x"], 5]).
        :param env: The current Environment.
        :param evaluator: A callback to the main ExpressionEvaluator.evaluate method.
        """
        pass
    