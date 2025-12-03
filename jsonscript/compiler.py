import re
from typing import List, Any, Optional

# --- 1. DEFINITION DES TOKENS ---
TOKEN_SPEC = [
    ('COMMENT', r'//.*'),
    ('STRING',  r'"[^"]*"'),
    ('NUMBER',  r'\d+'),
    # AJOUT DE 'import' DANS LES MOTS-CLÉS
    ('KEYWORD', r'\b(var|if|else|while|func|return|print|class|new|extends|import)\b'),
    ('ID',      r'[a-zA-Z_]\w*'),
    ('OP_CMP',  r'(==|!=|<=|>=|<|>)'),
    ('OP_MATH', r'[+\-*/%]'),
    ('ASSIGN',  r'='),
    ('LBRACE',  r'\{'),
    ('RBRACE',  r'\}'),
    ('LPAREN',  r'\('),
    ('RPAREN',  r'\)'),
    ('COMMA',   r','),
    ('DOT',     r'\.'),
    ('SKIP',    r'[ \t\n]+'),
    ('MISMATCH',r'.'),
]

class Token:
    def __init__(self, type_: str, value: str, line: int):
        self.type = type_
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.line_num = 1
        self.tokens = []

    def tokenize(self) -> List[Token]:
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)
        for mo in re.finditer(tok_regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP':
                self.line_num += value.count('\n')
                continue
            elif kind == 'COMMENT':
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Caractère inattendu '{value}' à la ligne {self.line_num}")
            if kind == 'STRING':
                value = value[1:-1]
            self.tokens.append(Token(kind, value, self.line_num))
        return self.tokens

# --- 2. LE PARSER ---
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> List[Any]:
        instructions = []
        while not self.is_at_end():
            instr = self.parse_statement()
            if instr:
                instructions.append(instr)
        return instructions

    # --- Helpers ---
    def peek(self, offset=0) -> Optional[Token]:
        if self.pos + offset >= len(self.tokens): return None
        return self.tokens[self.pos + offset]

    def consume(self, expected_type=None) -> Token:
        if self.is_at_end(): raise SyntaxError("Fin de fichier inattendue.")
        token = self.tokens[self.pos]
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Attendu {expected_type}, obtenu {token.type} ('{token.value}') ligne {token.line}")
        self.pos += 1
        return token

    def is_at_end(self):
        return self.pos >= len(self.tokens)

    def match(self, *types) -> bool:
        if self.is_at_end(): return False
        token = self.peek()
        if token and token.type in types:
            self.pos += 1
            return True
        return False

    def parse_params_list(self) -> List[str]:
        self.consume('LPAREN')
        params = []
        if not self.is_at_end() and self.peek().type != 'RPAREN':
            params.append(self.consume('ID').value)
            while self.match('COMMA'):
                params.append(self.consume('ID').value)
        self.consume('RPAREN')
        return params

    # --- Statements ---
    def parse_statement(self):
        token = self.peek()
        if token is None: return None

        if token.type == 'KEYWORD':
            if token.value == 'var':    return self.parse_var_decl()
            if token.value == 'print':  return self.parse_print()
            if token.value == 'if':     return self.parse_if()
            if token.value == 'while':  return self.parse_while()
            if token.value == 'func':   return self.parse_func()
            if token.value == 'return': return self.parse_return()
            if token.value == 'class':  return self.parse_class()
            # AJOUT: Gestion de l'import
            if token.value == 'import': return self.parse_import()
        
        if token.type == 'ID':
            next_tok = self.peek(1)
            if next_tok and next_tok.type == 'ASSIGN':
                name = self.consume('ID').value
                self.consume('ASSIGN')
                expr = self.parse_expression()
                return ["set", name, expr]
            return self.parse_expression()

        raise SyntaxError(f"Instruction inconnue '{token.value}' ligne {token.line}")

    def parse_block(self):
        self.consume('LBRACE')
        block = []
        while not self.is_at_end() and self.peek().type != 'RBRACE':
            block.append(self.parse_statement())
        self.consume('RBRACE')
        return block

    def parse_var_decl(self):
        self.consume() # var
        name = self.consume('ID').value
        self.consume('ASSIGN')
        expr = self.parse_expression()
        return ["set", name, expr]

    def parse_print(self):
        self.consume() # print
        expr = self.parse_expression()
        return ["print", expr]

    # AJOUT: Méthode parse_import
    def parse_import(self):
        self.consume() # import
        # On attend une chaîne de caractères (le nom du fichier)
        path = self.consume('STRING').value
        return ["import", path]

    def parse_if(self):
        self.consume()
        self.consume('LPAREN')
        condition = self.parse_expression()
        self.consume('RPAREN')
        true_block = self.parse_block()
        false_block = []
        if not self.is_at_end() and self.peek().type == 'KEYWORD' and self.peek().value == 'else':
            self.consume()
            if self.peek().value == 'if':
                false_block = [self.parse_if()]
            else:
                false_block = self.parse_block()
        return ["if", condition, true_block, false_block] if false_block else ["if", condition, true_block]

    def parse_while(self):
        self.consume()
        self.consume('LPAREN')
        condition = self.parse_expression()
        self.consume('RPAREN')
        body = self.parse_block()
        return ["while", condition, body]

    def parse_func(self):
        self.consume()
        name = self.consume('ID').value
        params = self.parse_params_list()
        body = self.parse_block()
        return ["function", name, params, body]

    def parse_class(self):
        self.consume()
        name = self.consume('ID').value
        params = self.parse_params_list()
        parent = None
        if not self.is_at_end() and self.peek().type == 'KEYWORD' and self.peek().value == 'extends':
            self.consume()
            parent = self.consume('ID').value
        self.consume('LBRACE')
        methods = {}
        while not self.is_at_end() and self.peek().type != 'RBRACE':
            m_name = self.consume('ID').value
            m_params = self.parse_params_list()
            m_body = self.parse_block()
            methods[m_name] = [m_params, m_body]
        self.consume('RBRACE')
        return ["class", name, params, methods, parent]

    def parse_return(self):
        self.consume()
        expr = self.parse_expression()
        return ["return", expr]

    # --- Expressions ---
    def parse_expression(self):
        return self.parse_logic()

    def parse_logic(self):
        left = self.parse_additive()
        while self.peek() and self.peek().type == 'OP_CMP':
            op = self.consume().value
            right = self.parse_additive()
            left = [op, left, right]
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.peek() and self.peek().type == 'OP_MATH' and self.peek().value in ('+', '-'):
            op = self.consume().value
            right = self.parse_multiplicative()
            if op == "+": left = ["+", left, right]
            elif op == "-": left = ["-", left, right]
        return left

    def parse_multiplicative(self):
        left = self.parse_primary()
        while self.peek() and self.peek().type == 'OP_MATH' and self.peek().value in ('*', '/', '%'):
            op = self.consume().value
            right = self.parse_primary()
            if op == "*": left = ["*", left, right]
            elif op == "/": left = ["/", left, right]
            elif op == "%": left = ["%", left, right]
        return left

    def parse_primary(self):
        token = self.peek()
        if token is None: raise SyntaxError("Fin de fichier inattendue.")

        if token.type == 'NUMBER':
            return int(self.consume().value)
        if token.type == 'STRING':
            return self.consume().value
        
        if token.type == 'ID':
            name = self.consume().value
            
            if self.match('LPAREN'):
                args = self.parse_args()
                self.consume('RPAREN')
                
                # LISTE DES COMMANDES NATIVES
                NATIVE_COMMANDS = [
                    # Maths
                    "sqrt", "pow", "abs", "round", "floor", "ceil", "random", "randint", "PI", "to_int",
                    # Strings
                    "split", "replace", "upper", "lower", "concat", "parse_json",
                    # Collection / Core
                    "len", "at", "type",
                    # Time
                    "now", "timestamp", "format_date",
                    # Sys / IO
                    "os_name", "cwd", "env", "exec", "read_file",
                    # Web
                    "http_get", "http_post"
                ]
                
                if name in NATIVE_COMMANDS:
                    return [name, *args]
                
                return ["call", name, *args]

            if self.match('DOT'):
                member = self.consume('ID').value
                if self.match('LPAREN'):
                    args = self.parse_args()
                    self.consume('RPAREN')
                    return ["call_method", ["get", name], member, *args]
                else:
                    return ["get_attr", ["get", name], member]

            return ["get", name]
            
        if token.type == 'KEYWORD' and token.value == 'new':
            self.consume()
            class_name = self.consume('ID').value
            self.consume('LPAREN')
            args = self.parse_args()
            self.consume('RPAREN')
            return ["new", class_name, *args]

        if self.match('LPAREN'):
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr

        raise SyntaxError(f"Expression invalide : {token.value} ligne {token.line}")

    def parse_args(self):
        args = []
        if not self.is_at_end() and self.peek().type != 'RPAREN':
            args.append(self.parse_expression())
            while self.match('COMMA'):
                args.append(self.parse_expression())
        return args

class JSSCompiler:
    def compile(self, source_code: str) -> List[Any]:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    