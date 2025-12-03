from typing import List, Any
from jsonscript.handlers.base import BaseHandler, EvaluatorFunc
from jsonscript.environment import Environment
from jsonscript.exceptions import ReturnValue


class ObjectHandler(BaseHandler):
    """
    Handles Object Oriented Programming: Instantiation, Method calls, Attributes.
    """
    def can_handle(self, command: str) -> bool:
        return command in {
            "new", 
            "call_method", 
            "get_attr", 
            "set_attr"
        }
    
    def handle(self, command: str, args: List[Any], env: Environment, evaluator: EvaluatorFunc) -> Any:
        
        # ["new", "ClassName", arg1, arg2...]
        if command == "new":
            class_name = args[0]
            constructor_args = args[1:]
            
            # 1. Récupérer la classe
            cls_def = env.get_class(class_name)
            
            # 2. Créer l'instance (C'est un dict avec un marqueur de type)
            instance = {
                "__class__": class_name,
                "__data__": {} # Les attributs seront stockés ici
            }
            
            # 3. Initialiser les attributs via le constructeur
            param_names = cls_def["params"]
            
            # Vérif arguments constructeur
            if len(constructor_args) != len(param_names):
                raise ValueError(f"Constructor for '{class_name}' expects {len(param_names)} args.")

            resolved_args = [evaluator(arg, env) for arg in constructor_args]
            
            # On remplit les données initiales
            for name, val in zip(param_names, resolved_args):
                instance["__data__"][name] = val
                
            return instance

        # ["get_attr", instance, "attr_name"]
        if command == "get_attr":
            instance = evaluator(args[0], env)
            attr_name = args[1] # String literal
            
            if not isinstance(instance, dict) or "__data__" not in instance:
                raise ValueError("Target is not a class instance.")
                
            return instance["__data__"].get(attr_name)

        # ["set_attr", instance, "attr_name", value]
        # Note: Ceci devrait idéalement être une Instruction, mais pour la simplicité on le met ici
        # (comme push/pop qui modifient en place)
        if command == "set_attr":
            instance = evaluator(args[0], env)
            attr_name = args[1]
            value = evaluator(args[2], env)
            
            if not isinstance(instance, dict) or "__data__" not in instance:
                raise ValueError("Target is not a class instance.")
            
            instance["__data__"][attr_name] = value
            return value # On retourne la valeur assignée

        # ["call_method", instance, "method_name", arg1...]
        if command == "call_method":
            # Local import
            from ..factory import InstructionFactory

            instance = evaluator(args[0], env)
            method_name = args[1]
            method_args = args[2:]
            
            if not isinstance(instance, dict) or "__class__" not in instance:
                raise ValueError("Target is not a valid object instance.")
            
            # 1. Trouver la définition de la méthode dans la classe
            class_name = instance["__class__"]
            cls_def = env.get_class(class_name)
            method_def = cls_def["methods"].get(method_name)
            
            if not method_def:
                raise ValueError(f"Method '{method_name}' not found in class '{class_name}'.")

            # 2. Préparer scope et arguments
            param_names = method_def["params"]
            if len(method_args) != len(param_names):
                raise ValueError(f"Method '{method_name}' expects {len(param_names)} args.")

            resolved_args = [evaluator(arg, env) for arg in method_args]

            env.enter_scope()
            
            # --- LA CLÉ EST ICI : On injecte 'this' ---
            env.set_variable("this", instance)
            
            for name, val in zip(param_names, resolved_args):
                env.set_variable(name, val)

            # 3. Exécution
            return_val = None
            try:
                for raw_inst in method_def["body"]:
                    InstructionFactory.build(raw_inst).execute(env)
            except ReturnValue as ret:
                return_val = ret.value
            finally:
                env.exit_scope()
            
            return return_val

        raise ValueError(f"ObjectHandler cannot handle: {command}")
    