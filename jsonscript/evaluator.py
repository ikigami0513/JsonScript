from typing import Any, List
from .environment import Environment

# Import des Handlers
from jsonscript.handlers.base import BaseHandler
from jsonscript.handlers.core import CoreHandler
from jsonscript.handlers.math import MathHandler
from jsonscript.handlers.string import StringHandler
from jsonscript.handlers.logic import LogicHandler
from jsonscript.handlers.collection import CollectionHandler
from jsonscript.handlers.io import IOHandler
from jsonscript.handlers.sys import SysHandler
from jsonscript.handlers.time import TimeHandler
from jsonscript.handlers.http import HttpHandler

class ExpressionEvaluator:
    # Enregistrement des Handlers
    _handlers: List[BaseHandler] = [
        CoreHandler(),
        MathHandler(),
        StringHandler(),
        LogicHandler(),
        CollectionHandler(),
        IOHandler(),
        SysHandler(),
        TimeHandler(),
        HttpHandler()
    ]

    @staticmethod
    def evaluate(expression: Any, environment: Environment) -> Any:
        # 1. Cas de base (Littéral)
        if not isinstance(expression, list):
            return expression
        
        if len(expression) == 0:
            return expression

        command = expression[0]
        arguments = expression[1:]

        # 2. Délégation au bon Handler
        for handler in ExpressionEvaluator._handlers:
            if handler.can_handle(command):
                return handler.handle(
                    command, 
                    arguments, 
                    environment, 
                    ExpressionEvaluator.evaluate # Callback récursif
                )

        # 3. Fallback (ex: une liste de données brutes [1, 2])
        return expression
    