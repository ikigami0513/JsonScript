import sys
import json
from jsonscript.runner import JsonScript
from jsonscript.factory import InstructionFactory
from jsonscript.environment import Environment
from jsonscript.compiler import JSSCompiler

def run_repl():
    """
    Read-Eval-Print Loop (Mode Interactif)
    Permet de taper des commandes JSON ligne par ligne.
    """
    print("Welcome to JsonScript v1.0 Interactive Shell")
    print("Type 'exit' to quit.")
    print("Example: [\"print\", \"Hello World\"]")
    
    # On garde l'environnement actif entre chaque ligne (pour garder les variables)
    env = Environment()

    while True:
        try:
            # 1. Read
            user_input = input("JS> ").strip()
            
            if user_input in ("exit", "quit"):
                break
            
            if not user_input:
                continue

            # 2. Parse (On espère recevoir une liste JSON valide)
            try:
                raw_instruction = json.loads(user_input)
            except json.JSONDecodeError:
                print("Error: Invalid JSON syntax.")
                continue

            if not isinstance(raw_instruction, list):
                print("Error: Input must be a JSON list (Array).")
                continue

            # 3. Eval & Execute
            # On construit une instruction à la volée et on l'exécute
            try:
                instruction = InstructionFactory.build(raw_instruction)
                instruction.execute(env)
            except Exception as e:
                print(f"Runtime Error: {e}")

        except KeyboardInterrupt:
            print("\nType 'exit' to quit.")
        except Exception as e:
            print(f"Shell Error: {e}")

def main():
    # Vérifie les arguments passés au script
    if len(sys.argv) > 1:
        # Mode Fichier : python main.py mon_fichier.json
        filename = sys.argv[1]

        if filename.endswith(".jss"):
            print(f"Compiling '{filename}'...")
            try:
                # Lecture
                with open(filename, "r", encoding="utf-8") as f:
                    source_code = f.read()
                
                # Compilation (JSS -> Liste d'instructions JSON)
                compiler = JSSCompiler()
                raw_instructions = compiler.compile(source_code)

                instructions_objects = [InstructionFactory.build(raw) for raw in raw_instructions]
                
                # Exécution directe (sans passer par from_file car on a déjà la liste)
                print("--- Running Compiled Code ---")
                JsonScript(instructions_objects).run()

            except FileNotFoundError:
                print(f"Error: File '{filename}' not found.")
            except Exception as e:
                print(f"Compilation/Execution Error: {e}")

        # 2. Cas fichier .json (Standard)
        else:
            JsonScript.from_file(filename).run()

    else:
        # Mode Interactif : python main.py
        run_repl()

if __name__ == "__main__":
    main()
    