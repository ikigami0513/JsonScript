import json
import time
from abc import ABC, abstractmethod
from jsonscript.environment import Environment
from jsonscript.evaluator import ExpressionEvaluator
from jsonscript.exceptions import ReturnValue
from typing import Any, List, Dict


# Abstract Base Class for all instructions
# This enforces that every instruction must have an 'execute' method
class Instruction(ABC):
    @abstractmethod
    def execute(self, environement: Environment):
        """Executes the logic associated with the instruction."""
        pass


class CommentInstruction(Instruction):
    def __init__(self, text: str):
        self.text = text # On garde le texte si jamais on veut faire du debug plus tard

    def execute(self, environment: Environment):
        # On ne fait rien du tout (No Operation)
        pass


class SetInstruction(Instruction):
    def __init__(self, name: str, value_expression: Any):
        self.name = name
        self.value_expression = value_expression

    def execute(self, environment: Environment):
        # We evaluate the expression at runtime to get the actual value
        resolved_value = ExpressionEvaluator.evaluate(self.value_expression, environment)
        environment.set_variable(self.name, resolved_value)


class PrintInstruction(Instruction):
    def __init__(self, args: List[Any]):
        self.args = args

    def execute(self, environment: Environment):
        resolved_values = []
        for arg in self.args:
            # Evaluate each argument (it could be a string "Text" or a ["get", "var"])
            val = ExpressionEvaluator.evaluate(arg, environment)
            resolved_values.append(str(val))
        
        # Join all parts and print
        print("".join(resolved_values))


class FunctionDefInstruction(Instruction):
    def __init__(self, name: str, params: List[str], body: List[Any]):
        self.name = name
        self.params = params
        self.body = body

    def execute(self, environment: Environment):
        environment.define_function(self.name, self.params, self.body)


class ReturnInstruction(Instruction):
    def __init__(self, value_expression: Any):
        self.value_expression = value_expression

    def execute(self, environment: Environment):
        # Evaluer la valeur à retourner
        val = ExpressionEvaluator.evaluate(self.value_expression, environment)
        # Lancer l'exception pour remonter la pile
        raise ReturnValue(val)


class CallInstruction(Instruction):
    def __init__(self, raw_expression: List[Any]):
        self.raw_expression = raw_expression # ["call", "name", arg1...]

    def execute(self, environment: Environment):
        # On délègue tout à l'évaluateur d'expression
        ExpressionEvaluator.evaluate(self.raw_expression, environment)


class WhileInstruction(Instruction):
    def __init__(self, condition: Any, body: List[Any]):
        self.condition = condition
        self.body = body

    def execute(self, environment: Environment):
        from jsonscript.factory import InstructionFactory

        # Loop while the condition evaluates to True
        while ExpressionEvaluator.evaluate(self.condition, environment):
            # Parse and execute the body logic
            for raw_instruction in self.body:
                InstructionFactory.build(raw_instruction).execute(environment)


class ForRangeInstruction(Instruction):
    def __init__(self, var_name: str, start: Any, end: Any, step: Any, body: List[Any]):
        self.var_name = var_name
        self.start_expr = start
        self.end_expr = end
        self.step_expr = step
        self.body = body

    def execute(self, environment: Environment):
        from jsonscript.factory import InstructionFactory

        # 1. Evaluate range parameters once at the beginning
        start_val = int(ExpressionEvaluator.evaluate(self.start_expr, environment))
        end_val = int(ExpressionEvaluator.evaluate(self.end_expr, environment))
        step_val = int(ExpressionEvaluator.evaluate(self.step_expr, environment))

        # 2. Iterate using Python's native range
        for i in range(start_val, end_val, step_val):
            # Update the loop variable in the environment
            environment.set_variable(self.var_name, i)
            
            # Execute body
            for raw_instruction in self.body:
                InstructionFactory.build(raw_instruction).execute(environment)


class IfInstruction(Instruction):
    def __init__(self, condition: Any, true_body: List[Any], false_body: List[Any] = None):
        self.condition = condition
        self.true_body = true_body
        self.false_body = false_body if false_body is not None else []

    def execute(self, environment: Environment):
        from jsonscript.factory import InstructionFactory

        # Evaluate the condition (expecting a boolean result)
        if ExpressionEvaluator.evaluate(self.condition, environment):
            # Execute the 'true' block
            for raw_instruction in self.true_body:
                InstructionFactory.build(raw_instruction).execute(environment)
        else:
            # Execute the 'else' block if it exists
            if self.false_body:
                for raw_instruction in self.false_body:
                    InstructionFactory.build(raw_instruction).execute(environment)


class PushInstruction(Instruction):
    def __init__(self, target_expression: Any, value_expression: Any):
        self.target_expression = target_expression
        self.value_expression = value_expression

    def execute(self, environment: Environment):
        target_list = ExpressionEvaluator.evaluate(self.target_expression, environment)
        if not isinstance(target_list, list):
            raise ValueError(f"Push error: Target is not a list. Got {type(target_list)}.")
        target_list.append(ExpressionEvaluator.evaluate(self.value_expression, environment))


class PutInstruction(Instruction):
    def __init__(self, target_expression: Any, key_expression: Any, value_expression: Any):
        self.target_expression = target_expression
        self.key_expression = key_expression
        self.value_expression = value_expression

    def execute(self, environment: Environment):
        # 1. Get the dict object
        target_dict = ExpressionEvaluator.evaluate(self.target_expression, environment)
        if not isinstance(target_dict, dict):
            raise ValueError(f"Put error: Target is not a dictionary. Got {type(target_dict)}.")
        
        # 2. Resolve Key and Value
        key = ExpressionEvaluator.evaluate(self.key_expression, environment)
        val = ExpressionEvaluator.evaluate(self.value_expression, environment)
        
        # 3. Update the dictionary
        target_dict[key] = val


class InputInstruction(Instruction):
    def __init__(self, var_name: str, prompt: str):
        self.var_name = var_name
        self.prompt = prompt

    def execute(self, environment: Environment):
        user_input = input(self.prompt)
        
        # Try to convert to int/float if possible, otherwise keep as string
        if user_input.isdigit():
            user_input = int(user_input)
        else:
            try:
                user_input = float(user_input)
            except ValueError:
                pass # Keep as string
                
        environment.set_variable(self.var_name, user_input)


class WriteFileInstruction(Instruction):
    def __init__(self, path_expr, content_expr):
        self.path_expr = path_expr
        self.content_expr = content_expr

    def execute(self, env):
        path = str(ExpressionEvaluator.evaluate(self.path_expr, env))
        content = str(ExpressionEvaluator.evaluate(self.content_expr, env))

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


class ImportInstruction(Instruction):
    def __init__(self, path_expression):
        self.path_expression = path_expression

    def execute(self, env):
        # 1. On évalue le chemin du fichier (permet de faire des imports dynamiques)
        filename = str(ExpressionEvaluator.evaluate(self.path_expression, env))
        
        # 2. Import local de la Factory pour éviter la boucle d'import
        from jsonscript.factory import InstructionFactory

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 3. On exécute chaque instruction du fichier importé
            # dans l'environnement *actuel* (env)
            for raw_item in data:
                InstructionFactory.build(raw_item).execute(env)

        except FileNotFoundError:
            print(f"Import Error: File '{filename}' not found.")
        except json.JSONDecodeError:
            print(f"Import Error: File '{filename}' is not valid JSON.")
        except Exception as e:
            print(f"Import Error in '{filename}': {e}")


class TryCatchInstruction(Instruction):
    def __init__(self, try_body: List[Any], error_var_name: str, catch_body: List[Any]):
        self.try_body = try_body
        self.error_var_name = error_var_name
        self.catch_body = catch_body

    def execute(self, environment: Environment):
        # Local import to avoid circular dependency
        from .factory import InstructionFactory

        try:
            # 1. Attempt to execute the instructions in the 'try' block
            for raw_instruction in self.try_body:
                InstructionFactory.build(raw_instruction).execute(environment)

        except ReturnValue:
            # CRITICAL: If a return happens inside the try block, 
            # we must NOT catch it as an error. We let it bubble up.
            raise

        except Exception as e:
            # 2. If an error occurs (DivByZero, FileNotFoud, etc.)
            # Store the error message in a variable
            environment.set_variable(self.error_var_name, str(e))
            
            # 3. Execute the 'catch' block
            for raw_instruction in self.catch_body:
                InstructionFactory.build(raw_instruction).execute(environment)


class SleepInstruction(Instruction):
    def __init__(self, duration_expression: Any):
        self.duration_expression = duration_expression

    def execute(self, environment: Environment):
        # On évalue l'expression (ça permet de faire sleep(variable))
        seconds = float(ExpressionEvaluator.evaluate(self.duration_expression, environment))
        time.sleep(seconds)


class ClassDefInstruction(Instruction):
    def __init__(self, name: str, init_params: List[str], methods: Dict[str, Any]):
        self.name = name
        self.init_params = init_params
        self.methods = methods

    def execute(self, environment: Environment):
        # On nettoie un peu le format des méthodes pour qu'il soit uniforme
        clean_methods = {}
        for method_name, method_data in self.methods.items():
            # method_data est une liste [ [params], [body] ]
            clean_methods[method_name] = {
                "params": method_data[0],
                "body": method_data[1]
            }
            
        environment.define_class(self.name, self.init_params, clean_methods)


class CallMethodInstruction(Instruction):
    def __init__(self, raw_expression: List[Any]):
        self.raw_expression = raw_expression

    def execute(self, environment: Environment):
        # On exécute l'expression pour déclencher la logique (et les side-effects)
        # On ignore la valeur de retour
        ExpressionEvaluator.evaluate(self.raw_expression, environment)

class SetAttrInstruction(Instruction):
    def __init__(self, raw_expression: List[Any]):
        self.raw_expression = raw_expression

    def execute(self, environment: Environment):
        # Idem, permet de faire ["set_attr", obj, "val", 10] sans le mettre dans un "set"
        ExpressionEvaluator.evaluate(self.raw_expression, environment)
