# JsonScript 🚀

JsonScript is an interpreted programming language, written in Python 3, that uses JSON as its syntax. It is Turing-complete, modular, object-oriented, and comes with a robust standard library (I/O, Networking, System, Math).

"Why write code when you can write data?"

---

## ✨ Features

- 100% JSON Syntax: Easy to parse, generate, and transmit programmatically.

- Turing-Complete: Supports Variables, Loops (while, for), Conditions (if/else), Functions (args, return).

- Object-Oriented: Classes, Instances, Inheritance, Polymorphism (this).

- Robust: Error handling (try/catch, throw, assert).

- Standard Library:

    - Math: sqrt, random, round, PI...

    - String: split, replace, concat, parse_json...

    - System: exec (shell), fs (read/write files), time, os.

    - Network: HTTP Client (get, post).

- Portable: No external dependencies (uses only Python standard library).

- Interoperable: Ability to inject native Python functions directly into the script environment.

---

## 📦 Installation & Usage
### Prerequisites

    Python 3.8+

### Running JsonScript

1. Interactive Mode (REPL) Launch a shell to type commands live.
Bash

```
python main.py
```

2. Execute a Script
Bash

```
python main.py my_script.json
```

---

## 📚 Syntax Guide

An instruction is always a List where the first element is the command. Example: `["command", arg1, arg2]`

1. Variables & Types

```json
["set", "x", 42]                   // Integer
["set", "name", "Alice"]           // String
["set", "users", ["Bob", "Eve"]]   // List
["set", "config", {"debug": true}] // Dictionary (Object)

["get", "x"]                       // Access a variable
```

2. Output & Input

```json
["print", "Hello ", ["get", "name"]]
["input", "age", "How old are you?"]
```

3. Logic & Control Flow

```json
// Condition
["if", [">", ["get", "x"], 10],
    [ ["print", "x is big"] ],   // True Block
    [ ["print", "x is small"] ]  // False Block (Optional)
]

// While Loop
["while", ["<", ["get", "i"], 5], [
    ["set", "i", ["+", ["get", "i"], 1]]
]]

// For Loop (Range): start, end, step
["for_range", "i", 0, 10, 2, [
    ["print", ["get", "i"]]
]]
```

4. Data Structures

```json
// Lists
["push", ["get", "my_list"], "New Item"]
["at", ["get", "my_list"], 0]    // Read index 0
["len", ["get", "my_list"]]      // Length

// Dictionaries
["put", ["get", "my_dict"], "key", "value"]
["at", ["get", "my_dict"], "key"]
```

5. Functions

```json
// Definition
["function", "add", ["a", "b"], [
    ["return", ["+", ["get", "a"], ["get", "b"]]]
]]

// Call
["set", "res", ["call", "add", 10, 20]]
```

6. Object-Oriented Programming (OOP)

```json
// Class Definition
["class", "Dog", ["name"], {
    "bark": [ [], [ ["print", "Woof!"] ] ]
}, "Animal"] // Optional Inheritance

// Instantiation
["set", "rex", ["new", "Dog", "Rex"]]

// Method Call
["call_method", ["get", "rex"], "bark"]

// Attributes (this)
["get_attr", ["get", "this"], "name"]
["set_attr", ["get", "this"], "hp", 100]
```

🛠 Standard Library (Expressions)

These commands return a value and can be nested inside other instructions.
| Category | Commands | Example |
| :--- | :--- | :--- |
| Math | `+`, `-`, `*`, `/`, `%` | `["+", 1, 2]` |
| Comparison | `==`, `!=`, `<`, `>`, `<=`, `>=` | `["==", ["get", "x"], 0]` |
| Advanced Math | `sqrt`, `pow`, `abs`, `round`, `floor`, `ceil`, `PI` | `["sqrt", 16]` |
| Random | `random`, `randint` | `["randint", 1, 6]` |
| String | `concat`, `split`, `replace`, `upper`, `lower` | `["upper", "text"]` |
| JSON | `parse_json` | `["parse_json", "{\"a\":1}"]` |
| Time | `now`, `timestamp`, `format_date` | `["now"]` |
| System | `os_name`, `cwd`, `env` | `["os_name"]` |
| Files | `read_file` | `["read_file", "log.txt"]` |
| Web | `http_get`, `http_post` | `["http_get", "https://api.co"]` |
| Meta | `type` | `["type", ["get", "x"]]` |

System Instructions (Do not return a value):

```json
    ["write_file", "path", "content"]

    ["exec", "command"] (Run a shell command)

    ["sleep", seconds]

    ["import", "lib.json"]

    ["throw", "Error message"]

    ["assert", condition, "Error message"]
```

## 🏗 Code Architecture

The project is designed with a modular architecture:

- `jsonscript/runner.py` : Entry point, orchestrates parsing and execution.
- `jsonscript/factory.py` : Instantiates Instruction objects.
- `jsonscript/environment.py` : Manages memory (scopes), functions, and classes.
- `jsonscript/instructions.py` : Logic for actions (While, If, Print...).
- `jsonscript/evaluator.py` : Router/Dispatcher for math/logic expressions.
- `jsonscript/handlers/` : Detailed implementation of operations (math, string, http, object...).

## 🤝 Contributing

- Fork the repository.
- Add a new Handler in jsonscript/handlers/.
- Register it in evaluator.py.
- Submit a Pull Request!
