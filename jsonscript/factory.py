from typing import List, Any
from jsonscript.instructions import * 


# Factory class to instantiate the correct object based on the raw JSON list
class InstructionFactory:
    @staticmethod
    def build(raw_instruction: List[Any]) -> Instruction:
        command_type = raw_instruction[0]

        if command_type == "comment":
            # On accepte ["comment"] ou ["comment", "texte"]
            text = raw_instruction[1] if len(raw_instruction) > 1 else ""
            return CommentInstruction(text)

        elif command_type == "set":
            # Syntax: ["set", "var_name", value_expression]
            # value_expression can be 4 or ["get", "other_var"]
            if len(raw_instruction) < 3:
                raise ValueError("Invalid parameters for 'set'.")
            return SetInstruction(name=raw_instruction[1], value_expression=raw_instruction[2])
        
        elif command_type == "print":
            # Syntax: ["print", arg1, arg2, ...]
            # Arguments start from index 1
            return PrintInstruction(args=raw_instruction[1:])
        
        elif command_type == "function":
            # Syntax: ["function", "name", ["arg1", "arg2"], [body]]
            if len(raw_instruction) < 4:
                raise ValueError("Invalid function definition.")
            return FunctionDefInstruction(name=raw_instruction[1], params=raw_instruction[2], body=raw_instruction[3])
        
        elif command_type == "return":
            # Syntax: ["return", value]
            return ReturnInstruction(raw_instruction[1])
        
        elif command_type == "call":
            # Syntax: ["call", "name"]
            if len(raw_instruction) < 2:
                raise ValueError("Invalid function call.")
            return CallInstruction(raw_instruction)
        
        elif command_type == "break":
            return BreakInstruction()
        
        elif command_type == "while":
            # Syntax: ["while", [condition expression], [ [inst1], [inst2] ]]
            if len(raw_instruction) < 3: raise ValueError("Invalid while loop.")
            return WhileInstruction(condition=raw_instruction[1], body=raw_instruction[2])
        
        elif command_type == "for_range":
            # Syntax: ["for_range", "var_name", start, end, step, [body]]
            if len(raw_instruction) < 6: raise ValueError("Invalid for_range loop.")
            return ForRangeInstruction(
                var_name=raw_instruction[1],
                start=raw_instruction[2],
                end=raw_instruction[3],
                step=raw_instruction[4],
                body=raw_instruction[5]
            )
        
        elif command_type == "if":
            # Syntax: ["if", condition, [true_block], [optional_false_block]]
            if len(raw_instruction) < 3:
                raise ValueError("Invalid 'if' instruction.")
            
            condition = raw_instruction[1]
            true_body = raw_instruction[2]
            
            # Check if there is an 'else' block (4th element)
            false_body = raw_instruction[3] if len(raw_instruction) > 3 else None
            
            return IfInstruction(condition, true_body, false_body)
        
        elif command_type == "push":
            # Syntax: ["push", ["get", "mylist"], value]
            return PushInstruction(target_expression=raw_instruction[1], value_expression=raw_instruction[2])
        
        elif command_type == "put":
            # Syntax: ["put", ["get", "mydict"], "key", "value"]
            if len(raw_instruction) < 4:
                raise ValueError("Invalid put.")
            return PutInstruction(target_expression=raw_instruction[1], key_expression=raw_instruction[2], value_expression=raw_instruction[3]) 
        
        elif command_type == "input":
            # Syntax: ["input", "target_var", "Prompt Text"]
            if len(raw_instruction) < 3: 
                raise ValueError("Invalid input.")
            return InputInstruction(var_name=raw_instruction[1], prompt=raw_instruction[2])
        
        elif command_type == "write_file":
            # Syntax: ["write_file", "path/to/file.txt", ["get", "content"]]
            if len(raw_instruction) < 3:
                raise ValueError("Invalid write_file.")
            return WriteFileInstruction(path_expr=raw_instruction[1], content_expr=raw_instruction[2])
        
        elif command_type == "import":
            # Syntax: ["import", "lib/math.json"]
            return ImportInstruction(path_expression=raw_instruction[1])
        
        elif command_type == "try":
            # Syntax: ["try", [body], "err_var", [catch_body]]
            if len(raw_instruction) < 4: 
                raise ValueError("Invalid try-catch block.")
            return TryCatchInstruction(
                try_body=raw_instruction[1], 
                error_var_name=raw_instruction[2], 
                catch_body=raw_instruction[3]
            )
        
        elif command_type == "sleep":
            # Syntax: ["sleep", 2] ou ["sleep", ["get", "delay"]]
            if len(raw_instruction) < 2: 
                raise ValueError("Invalid sleep instruction.")
            return SleepInstruction(raw_instruction[1])
        
        elif command_type == "class":
            # Syntax: ["class", "Name", ["attribute_1", "attribute_2"], { "method_1": [["params"], [body]] }]
            if len(raw_instruction) < 4:
                raise ValueError("Invalid class instruction")
            
            parent = raw_instruction[4] if len(raw_instruction) > 4 else None

            return ClassDefInstruction(name=raw_instruction[1], init_params=raw_instruction[2], methods=raw_instruction[3], parent_name=parent)
        
        elif command_type == "call_method":
            # ["call_method", obj, method, args...]
            return CallMethodInstruction(raw_expression=raw_instruction)
        
        elif command_type == "set_attr":
            # ["set_attr", obj, attr, val]
            return SetAttrInstruction(raw_expression=raw_instruction)
        
        elif command_type == "throw":
            # ["throw", "Message d'erreur"]
            return ThrowInstruction(message_expression=raw_instruction[1])
        
        elif command_type == "assert":
            # ["assert", condition, "Message si faux"]
            if len(raw_instruction) < 3: 
                raise ValueError("Invalid assert.")
            return AssertInstruction(condition=raw_instruction[1], error_message=raw_instruction[2])

        else:
            raise ValueError(f"Unknown command: {command_type}")
        