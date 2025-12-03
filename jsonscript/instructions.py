import json
import time
from abc import ABC, abstractmethod
from jsonscript.environment import Environment
from jsonscript.evaluator import ExpressionEvaluator
from jsonscript.exceptions import BreakLoop, ReturnValue
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


class BreakInstruction(Instruction):
    def __init__(self):
        pass

    def execute(self, environment: Environment):
        # On lève l'exception pour signaler l'arrêt immédiat
        raise BreakLoop()


class WhileInstruction(Instruction):
    def __init__(self, condition: Any, body: List[Any]):
        self.condition = condition
        self.body = body

    def execute(self, environment: Environment):
        from .factory import InstructionFactory # Local import
        
        # On enveloppe toute la boucle dans un try/except
        try:
            while ExpressionEvaluator.evaluate(self.condition, environment):
                for raw_instruction in self.body:
                    InstructionFactory.build(raw_instruction).execute(environment)
        except BreakLoop:
            # Si un 'break' est levé, on atterrit ici.
            # On ne fait rien (pass), ce qui permet de continuer le script APRES la boucle.
            pass


class ForRangeInstruction(Instruction):
    def __init__(self, var_name: str, start: Any, end: Any, step: Any, body: List[Any]):
        self.var_name = var_name
        self.start_expr = start
        self.end_expr = end
        self.step_expr = step
        self.body = body

    def execute(self, environment: Environment):
        from .factory import InstructionFactory # Local import
        
        start_val = int(ExpressionEvaluator.evaluate(self.start_expr, environment))
        end_val = int(ExpressionEvaluator.evaluate(self.end_expr, environment))
        step_val = int(ExpressionEvaluator.evaluate(self.step_expr, environment))

        try:
            for i in range(start_val, end_val, step_val):
                environment.set_variable(self.var_name, i)
                for raw_instruction in self.body:
                    InstructionFactory.build(raw_instruction).execute(environment)
        except BreakLoop:
            pass # On sort proprement de la boucle for


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


class ImportInstruction(Instruction):
    def __init__(self, path_expression):
        self.path_expression = path_expression

    def execute(self, env):
        # 1. On résout le chemin du fichier
        filename = str(ExpressionEvaluator.evaluate(self.path_expression, env))
        
        # Imports locaux pour éviter les cycles
        from jsonscript.factory import InstructionFactory
        
        try:
            raw_instructions = []

            # --- CAS 1 : Fichier JSS  ---
            if filename.endswith(".jss"):
                from jsonscript.compiler import JSSCompiler # Import local du compilateur
                with open(filename, "r", encoding="utf-8") as f:
                    source_code = f.read()
                
                # On compile à la volée
                compiler = JSSCompiler()
                raw_instructions = compiler.compile(source_code)

            # --- CAS 2 : Fichier JSON (Legacy) ---
            else:
                import json
                with open(filename, "r", encoding="utf-8") as f:
                    raw_instructions = json.load(f)
                print(f"DEBUG: Importing JSON module '{filename}'...")
            
            # 3. Exécution des instructions importées dans l'environnement actuel
            for raw_item in raw_instructions:
                InstructionFactory.build(raw_item).execute(env)

        except FileNotFoundError:
            print(f"Import Error: File '{filename}' not found.")
        except Exception as e:
            # Affiche l'erreur complète pour le debug
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
    def __init__(self, name: str, init_params: List[str], methods: Dict[str, Any], parent_name: str = None):
        self.name = name
        self.init_params = init_params
        self.methods = methods
        self.parent_name = parent_name

    def execute(self, environment: Environment):
        # On nettoie un peu le format des méthodes pour qu'il soit uniforme
        clean_methods = {}
        for method_name, method_data in self.methods.items():
            # method_data est une liste [ [params], [body] ]
            clean_methods[method_name] = {
                "params": method_data[0],
                "body": method_data[1]
            }
            
        environment.define_class(self.name, self.init_params, clean_methods, self.parent_name)


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


class ThrowInstruction(Instruction):
    def __init__(self, message_expression: Any):
        self.message_expression = message_expression

    def execute(self, environment: Environment):
        # On évalue le message d'erreur
        msg = str(ExpressionEvaluator.evaluate(self.message_expression, environment))
        # On lève une exception Python standard. 
        # Ton TryCatchInstruction existant l'attrapera automatiquement !
        raise RuntimeError(msg)

class AssertInstruction(Instruction):
    def __init__(self, condition: Any, error_message: Any):
        self.condition = condition
        self.error_message = error_message

    def execute(self, environment: Environment):
        # Si la condition est FAUSSE, on lève l'erreur
        if not ExpressionEvaluator.evaluate(self.condition, environment):
            msg = str(ExpressionEvaluator.evaluate(self.error_message, environment))
            raise AssertionError(f"Assertion Failed: {msg}")


class SwitchInstruction(Instruction):
    def __init__(self, test_expr: Any, cases: List[List[Any]], default_block: List[Any] = None):
        self.test_expr = test_expr
        self.cases = cases # Liste de paires [ [valeur_declencheur, [instructions]], ... ]
        self.default_block = default_block if default_block is not None else []

    def execute(self, environment: Environment):
        # Local import
        from .factory import InstructionFactory

        # 1. On évalue la valeur qu'on teste (ex: "admin")
        test_val = ExpressionEvaluator.evaluate(self.test_expr, environment)
        
        match_found = False

        # 2. On parcourt les cas
        for case_entry in self.cases:
            case_val_expr = case_entry[0]
            case_body = case_entry[1]
            
            # On évalue la valeur du case (permet de faire case 1+1:)
            case_val = ExpressionEvaluator.evaluate(case_val_expr, environment)
            
            if test_val == case_val:
                match_found = True
                # Exécution du bloc correspondant
                for raw_inst in case_body:
                    InstructionFactory.build(raw_inst).execute(environment)
                return # On sort du switch (comportement moderne)

        # 3. Si aucun cas ne correspond, on lance le default
        if not match_found and self.default_block:
            for raw_inst in self.default_block:
                InstructionFactory.build(raw_inst).execute(environment)


class ExpressionInstruction(Instruction):
    """
    Executes a standalone expression (e.g. ["fs_mkdir", "path"] or ["exec", "cmd"]).
    Useful for native commands that have side effects but no return value capture.
    """
    def __init__(self, raw_expression: List[Any]):
        self.raw_expression = raw_expression

    def execute(self, environment: Environment):
        # On utilise l'évaluateur pour exécuter la logique
        ExpressionEvaluator.evaluate(self.raw_expression, environment)
