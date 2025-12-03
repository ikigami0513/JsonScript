import json
from typing import List, Optional
from jsonscript.environment import Environment
from jsonscript.instructions import Instruction
from jsonscript.factory import InstructionFactory
from jsonscript.exceptions import ReturnValue


class JsonScript:
    def __init__(self, instructions: List[Instruction]):
        self.instructions = instructions

    def run(self, environment: Optional[Environment] = None) -> Environment:
        env = environment if environment is not None else Environment()

        try:
            for i in self.instructions:
                i.execute(env)
        except ReturnValue:
            print("Error: 'return' used outside of a function.")
        except Exception as e:
            print(f"Runtime Error: {e}")

        return env
    
    @classmethod
    def from_file(cls, filename: str) -> 'JsonScript':
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls([InstructionFactory.build(x) for x in data])
        except Exception as e:
            print(f"Loading Error: {e}")
            return cls([])
        