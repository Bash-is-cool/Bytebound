import re

# =============================================================================
# 1. LEXER (TOKENIZATION ENGINE)
# =============================================================================
class Token:
    """Represents an atomic semantic element in our scripting syntax."""
    def __init__(self, type_, value=None):
        self.type = type_      # Category (e.g., 'KEYWORD', 'IDENTIFIER', 'OPERATOR')
        self.value = value     # Literal contents (e.g., 'walk', 'if', '==')
        
    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    """Breaks raw text strings down into structural token sequence flows."""
    # Added 'elif' and 'else' to the structural keywords group
    TOKEN_SPECIFICATION = [
        ('NUMBER',     r'\d+'),                     # Integer values
        ('COLON',      r':'),                       # Separation boundaries
        ('COMP',       r'==|!=|<=|>=|<|>'),         # Relational logic
        ('ASSIGN',     r'='),                       # Base assignments
        ('KEYWORD',    r'\b(if|elif|else|and|or|not)\b'), # Logic statements
        ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'), # Names, commands, environment variables
        ('SKIP',       r'[ \t\r\n]+'),              # Whitespace compression
        ('MISMATCH',   r'.'),                       # Error fallback catchers
    ]
    
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        
    def tokenize(self):
        regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.TOKEN_SPECIFICATION)
        for mo in re.finditer(regex, self.source_code):
            kind = mo.lastgroup
            value = mo.group(kind)
            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Unexpected character pattern sequence: {value}")
            self.tokens.append(Token(kind, value))
        return self.tokens

# =============================================================================
# 2. BOOLEAN ABSTRACT SYNTAX TREE (AST) PARSER
# =============================================================================
class BooleanParser:
    """
    Parses token loops using recursive descent matching standard operator precedence:
    Level 1 (Lowest):  OR
    Level 2:          AND
    Level 3 (Highest): Base Comparisons (==, !=, <, etc.)
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type=None):
        tok = self.peek()
        if not tok:
            raise SyntaxError("Unexpected End of Script line stream encountered.")
        if expected_type and tok.type != expected_type:
            raise SyntaxError(f"Expected token {expected_type}, got {tok.type}")
        self.pos += 1
        return tok

    def parse_expression(self):
        """Entry point: evaluates low precedence OR equations."""
        node = self.parse_and_term()
        while self.peek() and self.peek().value == "or":
            self.consume()
            right_node = self.parse_and_term()
            node = ('OR', node, right_node)
        return node

    def parse_and_term(self):
        """Evaluates medium precedence AND equations."""
        node = self.parse_factor()
        while self.peek() and self.peek().value == "and":
            self.consume()
            right_node = self.parse_factor()
            node = ('AND', node, right_node)
        return node

    def parse_factor(self):
        """Evaluates base variable declarations and scalar binary comparisons."""
        left_tok = self.consume('IDENTIFIER')
        
        next_tok = self.peek()
        if next_tok and next_tok.type == 'COMP':
            op_tok = self.consume('COMP')
            right_tok = self.consume() 
            return ('COMPARE', left_tok.value, op_tok.value, right_tok.value)
        
        return ('BOOLEAN_VARIABLE', left_tok.value)


# =============================================================================
# 3. INTERPRETER EXECUTION CONTAINER
# =============================================================================
class TokenInterpreter:
    def __init__(self):
        self.output_history = []
        # Tracks structural execution state across line sweeps
        # None = No structural block active right now
        # True = A conditional in this block has run (skip subsequent elif/else)
        # False = No conditional in this block has met criteria yet (eligible to run)
        self.last_if_state = None
        
    def evaluate_ast(self, node, game_environment):
        """Recursively resolves Abstract Syntax Trees into Boolean states."""
        node_type = node[0]
        
        if node_type == 'OR':
            return self.evaluate_ast(node[1], game_environment) or self.evaluate_ast(node[2], game_environment)
            
        elif node_type == 'AND':
            return self.evaluate_ast(node[1], game_environment) and self.evaluate_ast(node[2], game_environment)
            
        elif node_type == 'COMPARE':
            _, left_var, operator, right_val = node
            left_val = game_environment.get(left_var, 0)
            
            if str(right_val).isdigit():
                right_val = int(right_val)
                
            if operator == '==': return left_val == right_val
            if operator == '!=': return left_val != right_val
            if operator == '<':  return left_val < right_val
            if operator == '>':  return left_val > right_val
            if operator == '<=': return left_val <= right_val
            if operator == '>=': return left_val >= right_val
            
        elif node_type == 'BOOLEAN_VARIABLE':
            return bool(game_environment.get(node[1], False))
            
        return False

    def execute_line(self, raw_line, game_environment, action_queue):
        """Processes a single line text code payload supporting IF/ELIF/ELSE structures."""
        line = raw_line.strip()
        if not line or line.startswith("#"):
            return

        try:
            # Step 1: Lexical Breakdown Analysis 
            lexer = Lexer(line)
            tokens = lexer.tokenize()
            
            if not tokens:
                return

            first_token = tokens[0]
            execution_tokens = []

            # Step 2: Complex Block Condition Routing Matrices
            if first_token.type == 'KEYWORD' and first_token.value in ('if', 'elif', 'else'):
                colon_idx = next((i for i, t in enumerate(tokens) if t.type == 'COLON'), None)
                if colon_idx is None:
                    self.output_history.append(f"[Syntax Error]: Missing structural assignment boundary ':'")
                    return
                
                condition_tokens = tokens[1:colon_idx]
                execution_tokens = tokens[colon_idx + 1:]

                # --- IF BLOCK INITIALIZATION ---
                if first_token.value == 'if':
                    # Reset cross-line track state to False since a new chain has started
                    self.last_if_state = False 
                    
                    boolean_parser = BooleanParser(condition_tokens)
                    ast_tree = boolean_parser.parse_expression()
                    
                    if self.evaluate_ast(ast_tree, game_environment):
                        self.last_if_state = True # Met. Set tracking flag so elif/else ignore line passes
                    else:
                        return # Condition failed. Drop execution.

                # --- ELIF BLOCK STEP SWEEPS ---
                elif first_token.value == 'elif':
                    if self.last_if_state is None:
                        self.output_history.append("[Syntax Error]: 'elif' statement found without matching 'if' parent context.")
                        return
                    
                    # If any preceding part of this block chain has already passed, skip completely
                    if self.last_if_state == True:
                        return 
                    
                    boolean_parser = BooleanParser(condition_tokens)
                    ast_tree = boolean_parser.parse_expression()
                    
                    if self.evaluate_ast(ast_tree, game_environment):
                        self.last_if_state = True
                    else:
                        return # Condition failed. Drop execution.

                # --- ELSE FALLBACK HANDLING ---
                elif first_token.value == 'else':
                    if self.last_if_state is None:
                        self.output_history.append("[Syntax Error]: 'else' statement found without matching parent 'if'.")
                        return
                    
                    if condition_tokens:
                        self.output_history.append("[Syntax Error]: 'else' statements cannot accept structural evaluation conditions.")
                        return
                    
                    # If an 'if' or 'elif' took action already, skip this block fallback rule safely
                    if self.last_if_state == True:
                        return
                    
                    # Consume state because the else block is finalized
                    self.last_if_state = None

            else:
                # Standard raw baseline command line rule. Clear block contexts.
                self.last_if_state = None
                execution_tokens = tokens

            # Step 3: Run Command Parser Payload
            if not execution_tokens:
                return
                
            command = execution_tokens[0].value.lower()
            cmd_args = [t.value for t in execution_tokens[1:]]

            if command == "walk":
                if len(cmd_args) < 2: raise ValueError("'walk' requires direction and distance parameters.")
                direction = cmd_args[0].lower()
                distance = int(cmd_args[1])
                action_queue.append(("walk", direction, distance))
                self.output_history.append(f"[Queue Success]: Added walk -> {direction} ({distance} frames)")
                
            elif command in ("build", "destroy"):
                if len(cmd_args) < 2: raise ValueError(f"'{command}' requires direction and length configuration metrics.")
                direction = cmd_args[0].lower()
                hold_time = int(cmd_args[1])
                action_queue.append((command, direction, hold_time))
                self.output_history.append(f"[Queue Success]: Added {command} -> {direction} ({hold_time} duration)")
                
            else:
                self.output_history.append(f"[Runtime Error]: Command identifier '{command}' could not be routed.")

        except Exception as err:
            self.output_history.append(f"[Parser Fault]: Failure Processing Line -> {str(err)}")