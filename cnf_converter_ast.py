"""
    THIS CODE HAS BEEN DEVELOPED WITH THE USE OF AI ASSISTANCE.

    An alternative can be found in the cnf_converter.py file.

    This version uses an AST (Abstract Syntax Tree) to represent the formula.
    The cnf_converter.py version uses a string representation of the formula.
"""


from copy import deepcopy # For checking convergence in distribution

# --- AST Node Definitions ---

class Formula:
    """Base class for all formula AST nodes."""
    def __eq__(self, other):
        # Structural equality check
        return isinstance(other, type(self)) and self.__dict__ == other.__dict__

    def __hash__(self):
        # Simple hash based on representation; ensure subclasses implement __repr__ well
        return hash(repr(self))

    def __repr__(self):
        raise NotImplementedError("Subclasses must implement __repr__")

class Literal(Formula):
    def __init__(self, name):
        if not isinstance(name, str) or not name.replace('_', '').isalnum() or name[0].isdigit():
            # Allow letters, numbers, underscores, but not starting with a digit
            raise ValueError(f"Invalid literal name: '{name}'")
        self.name = name

    def __repr__(self):
        return self.name

class Not(Formula):
    def __init__(self, operand):
        if not isinstance(operand, Formula):
             raise TypeError("Operand must be a Formula instance")
        self.operand = operand

    def __repr__(self):
        op_repr = repr(self.operand)
        # Add parentheses if operand is a binary operation to avoid ambiguity like ¬A ∧ B
        if isinstance(self.operand, (And, Or, Implies, Iff)):
             return f"¬({op_repr})"
        # No parentheses needed for ¬¬A or ¬A
        return f"¬{op_repr}"

class BinaryOp(Formula):
    """Base class for binary operators."""
    def __init__(self, left, right, symbol):
        if not isinstance(left, Formula) or not isinstance(right, Formula):
            raise TypeError("Operands must be Formula instances")
        self.left = left
        self.right = right
        self.symbol = symbol # For representation

    def __repr__(self):
        # Add parentheses around operands if they are binary ops of lower/equal precedence
        # Simplification: Add parentheses around *any* binary operand for clarity
        left_repr = repr(self.left)
        if isinstance(self.left, BinaryOp):
             left_repr = f"({left_repr})"

        right_repr = repr(self.right)
        if isinstance(self.right, BinaryOp):
             right_repr = f"({right_repr})"

        return f"{left_repr} {self.symbol} {right_repr}"

class And(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, right, "∧")

class Or(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, right, "∨")

class Implies(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, right, "→")

class Iff(BinaryOp):
    def __init__(self, left, right):
        super().__init__(left, right, "↔")


# --- Parser (Recursive Descent) ---
# Handles precedence: ¬ > ∧ > ∨ > → > ↔

class Parser:
    def __init__(self, formula_string):
        # Normalize input string: Add spaces around operators and parentheses
        # for easier tokenization. Remove redundant spaces.
        s = formula_string.strip()
        for op in ["↔", "→", "∨", "∧", "¬", "(", ")"]:
            s = s.replace(op, f" {op} ")
        self.tokens = [token for token in s.split() if token] # Basic tokenizer
        self.pos = 0
        # print(f"Tokens: {self.tokens}") # Debugging

    def parse(self) -> Formula:
        if not self.tokens:
            raise ValueError("Cannot parse empty formula")
        formula = self._parse_iff()
        if self.pos < len(self.tokens):
            # If not all tokens were consumed, likely a syntax error
            raise ValueError(f"Unexpected token '{self.tokens[self.pos]}' at position {self.pos}")
        return formula

    def _current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _consume(self, expected_token=None):
        token = self._current_token()
        if expected_token and token != expected_token:
            raise ValueError(f"Expected '{expected_token}' but found '{token}' at position {self.pos}")
        if token is None:
            raise ValueError("Unexpected end of formula")
        self.pos += 1
        return token

    # Parse based on precedence (lowest first)
    def _parse_iff(self):
        left = self._parse_implies()
        while self._current_token() == "↔":
            self._consume("↔")
            right = self._parse_implies()
            left = Iff(left, right)
        return left

    def _parse_implies(self):
        left = self._parse_or()
        while self._current_token() == "→":
            self._consume("→")
            right = self._parse_or()
            left = Implies(left, right)
        return left

    def _parse_or(self):
        left = self._parse_and()
        while self._current_token() == "∨":
            self._consume("∨")
            right = self._parse_and()
            left = Or(left, right)
        return left

    def _parse_and(self):
        left = self._parse_not() # Or parse_factor if not is highest precedence
        while self._current_token() == "∧":
            self._consume("∧")
            right = self._parse_not() # Or parse_factor
            left = And(left, right)
        return left

    def _parse_not(self):
        if self._current_token() == "¬":
            self._consume("¬")
            operand = self._parse_not() # Allows for stacked negations like ¬¬A
            return Not(operand)
        return self._parse_factor()

    # Parse literals and parenthesized expressions
    def _parse_factor(self):
        token = self._current_token()
        if token == "(":
            self._consume("(")
            expr = self._parse_iff() # Start parsing from the lowest precedence inside parens
            self._consume(")")
            return expr
        elif token is None:
             raise ValueError("Unexpected end of input, expected literal or '('")
        elif token in ["∧", "∨", "→", "↔", ")"]:
            raise ValueError(f"Unexpected operator '{token}' at position {self.pos}, expected literal or '('")
        else:
            # Assume it's a literal
            self._consume()
            try:
                return Literal(token)
            except ValueError as e:
                # Catch invalid literal names from Literal constructor
                raise ValueError(f"Invalid literal name '{token}' at position {self.pos - 1}: {e}")


# --- AST Transformation Functions ---

def eliminate_iff_ast(formula: Formula) -> Formula:
    """Step 1: Eliminate ↔ using (A → B) ∧ (B → A)"""
    if isinstance(formula, Literal):
        return formula
    elif isinstance(formula, Not):
        return Not(eliminate_iff_ast(formula.operand))
    elif isinstance(formula, (And, Or, Implies)):
        # Recursively apply to children
        return type(formula)(eliminate_iff_ast(formula.left),
                             eliminate_iff_ast(formula.right))
    elif isinstance(formula, Iff):
        # A ↔ B => (A → B) ∧ (B → A)
        left = formula.left
        right = formula.right
        # Recursively apply to the components *before* creating the new structure
        left_elim = eliminate_iff_ast(left)
        right_elim = eliminate_iff_ast(right)
        imp1 = Implies(left_elim, right_elim)
        imp2 = Implies(right_elim, left_elim)
        # Important: Recursively apply to the *newly created* structure too
        # Although eliminate_iff won't find more IFFs here, it's good practice
        # for consistency with other recursive transformations.
        return eliminate_iff_ast(And(imp1, imp2))
    else:
        raise TypeError(f"Unknown formula type: {type(formula)}")


def eliminate_imp_ast(formula: Formula) -> Formula:
    """Step 2: Eliminate → using ¬A ∨ B"""
    if isinstance(formula, Literal):
        return formula
    elif isinstance(formula, Not):
        return Not(eliminate_imp_ast(formula.operand))
    elif isinstance(formula, (And, Or)):
        return type(formula)(eliminate_imp_ast(formula.left),
                             eliminate_imp_ast(formula.right))
    elif isinstance(formula, Implies):
        # A → B => ¬A ∨ B
        left = formula.left
        right = formula.right
        # Recursively apply to components *before* creating the new structure
        left_elim = eliminate_imp_ast(left)
        right_elim = eliminate_imp_ast(right)
        # Important: Recursively apply to the result of the transformation
        return eliminate_imp_ast(Or(Not(left_elim), right_elim))
    # Note: Iff should have been eliminated already, but handle defensively
    elif isinstance(formula, Iff):
         raise TypeError("Implication elimination run before IFF elimination finished.")
    else:
        raise TypeError(f"Unknown formula type: {type(formula)}")


def move_negation_inwards_ast(formula: Formula) -> Formula:
    """Step 3: Move ¬ inwards (NNF) using De Morgan's and double negation"""
    if isinstance(formula, Literal):
        return formula
    elif isinstance(formula, And):
        return And(move_negation_inwards_ast(formula.left),
                   move_negation_inwards_ast(formula.right))
    elif isinstance(formula, Or):
         return Or(move_negation_inwards_ast(formula.left),
                   move_negation_inwards_ast(formula.right))
    elif isinstance(formula, Not):
        operand = formula.operand
        if isinstance(operand, Literal):
            return formula # ¬ is already innermost
        elif isinstance(operand, Not):
            # ¬¬A => A
            # Recursively apply to the inner part A
            return move_negation_inwards_ast(operand.operand)
        elif isinstance(operand, And):
            # ¬(A ∧ B) => ¬A ∨ ¬B
            # Recursively apply to the newly formed structure
            return move_negation_inwards_ast(
                Or(Not(operand.left), Not(operand.right))
            )
        elif isinstance(operand, Or):
            # ¬(A ∨ B) => ¬A ∧ ¬B
             # Recursively apply to the newly formed structure
            return move_negation_inwards_ast(
                And(Not(operand.left), Not(operand.right))
            )
        # Note: Implies and Iff should be gone, but handle defensively
        elif isinstance(operand, (Implies, Iff)):
             raise TypeError("NNF transformation run before implications/iff eliminated.")
        else:
            raise TypeError(f"Unknown formula type inside Not: {type(operand)}")
    # Note: Implies and Iff should be gone, but handle defensively
    elif isinstance(formula, (Implies, Iff)):
        raise TypeError("NNF transformation run before implications/iff eliminated.")
    else:
        raise TypeError(f"Unknown formula type: {type(formula)}")


def distribute_or_over_and_ast(formula: Formula) -> Formula:
    """Step 4: Distribute ∨ over ∧"""
    if isinstance(formula, (Literal, Not)):
        return formula # Base case

    if isinstance(formula, And):
        # Distribute in children first
        left = distribute_or_over_and_ast(formula.left)
        right = distribute_or_over_and_ast(formula.right)
        return And(left, right)

    if isinstance(formula, Or):
        # Distribute in children first
        left = distribute_or_over_and_ast(formula.left)
        right = distribute_or_over_and_ast(formula.right)

        # Check for distribution: A ∨ (B ∧ C) => (A ∨ B) ∧ (A ∨ C)
        if isinstance(right, And):
            # Create the two new OR clauses
            new_left_or = Or(left, right.left)
            new_right_or = Or(left, right.right)
            # Combine them with AND
            new_and = And(new_left_or, new_right_or)
            # VERY IMPORTANT: Recursively distribute within the *newly created* structure
            return distribute_or_over_and_ast(new_and)

        # Check for distribution: (A ∧ B) ∨ C => (A ∨ C) ∧ (B ∨ C)
        if isinstance(left, And):
            # Create the two new OR clauses
            new_left_or = Or(left.left, right)
            new_right_or = Or(left.right, right)
            # Combine them with AND
            new_and = And(new_left_or, new_right_or)
             # VERY IMPORTANT: Recursively distribute within the *newly created* structure
            return distribute_or_over_and_ast(new_and)

        # If no distribution rule applied at this level, return the potentially
        # transformed children within the Or node
        return Or(left, right)

    # Note: Implies, Iff, Not should not be the top-level operator here if NNF was correct
    else:
         raise TypeError(f"Unexpected formula type during distribution: {type(formula)}")


def extract_literals_from_clause(clause_node: Formula) -> set[str]:
    """
    Recursively extracts all literals (as strings) from an AST node
    representing a single clause (a disjunction of literals, or a single literal).
    """
    literals_set = set()

    def collect(node: Formula):
        if isinstance(node, Or):
            # Recursively collect from both sides of the disjunction
            collect(node.left)
            collect(node.right)
        elif isinstance(node, Literal):
            # Base case: found a positive literal
            literals_set.add(repr(node))
        elif isinstance(node, Not) and isinstance(node.operand, Literal):
            # Base case: found a negative literal
            literals_set.add(repr(node))
        elif isinstance(node, Not) and not isinstance(node.operand, Literal):
             # This shouldn't happen in a valid NNF/CNF clause
             raise TypeError(f"Invalid CNF clause structure: Found Not({type(node.operand)})")
        else:
             # This shouldn't happen in a valid CNF clause (e.g., finding an And)
             raise TypeError(f"Invalid CNF clause structure: Found unexpected node type {type(node)}")

    collect(clause_node)
    return literals_set


def cnf_ast_to_clauses(cnf_ast: Formula) -> list[set[str]]:
    """
    Converts a CNF formula AST into a list of clauses.
    Each clause is represented as a set of literal strings.

    Assumes the input AST is the result of the CNF conversion process
    (a conjunction of disjunctions of literals).
    """
    clauses_list = []

    def find_conjuncts(node: Formula):
        """Recursively traverses the AND nodes to find individual clauses."""
        if isinstance(node, And):
            # Explore both branches of the conjunction
            find_conjuncts(node.left)
            find_conjuncts(node.right)
        # If it's not an And, it must be a clause (Or, Literal, or Not)
        # Note: A valid CNF formula shouldn't contain Implies/Iff here.
        elif isinstance(node, (Or, Literal, Not)):
            try:
                clause_literals = extract_literals_from_clause(node)
                if clause_literals: # Avoid adding empty sets if something weird happens
                    clauses_list.append(clause_literals)
            except TypeError as e:
                # Propagate errors from literal extraction
                raise TypeError(f"Error extracting literals from potential clause node {node}: {e}")
        else:
             # Should not encounter other types like Implies/Iff at the top level of CNF
             raise TypeError(f"Unexpected node type in CNF structure: {type(node)}")

    # Handle the edge case of an empty input or a formula that somehow reduces
    # to a non-standard node type (though this shouldn't happen with the main converter)
    if not isinstance(cnf_ast, Formula):
         # Or perhaps return [] or raise error depending on desired behavior for invalid input
         return []

    find_conjuncts(cnf_ast)

    # If the original formula was just a single clause (no 'And' nodes),
    # find_conjuncts would have added it directly. If it was empty or invalid,
    # the list might be empty.

    return clauses_list


# --- CNF Conversion Orchestrator ---

def to_cnf(formula_string: str, return_ast=False) -> Formula | str:
    """
    Converts a propositional logic formula string to CNF.
    Returns the CNF as a string by default, or the final AST if return_ast is True.
    """
    # 1. Parse the input string into an AST
    try:
        parser = Parser(formula_string)
        ast = parser.parse()
    except ValueError as e:
        # Returning error string directly if parsing fails
        error_msg = f"Error parsing formula: {e}"
        if return_ast:
            # Can't return an AST if parsing failed, maybe raise exception or return None?
            # For consistency let's raise here if AST was expected.
            raise ValueError(error_msg)
        return error_msg
    except TypeError as e:
         # Returning error string directly if AST node creation fails
        error_msg = f"Error during AST node creation: {e}"
        if return_ast:
            raise TypeError(error_msg) # Raise if AST was expected
        return error_msg

    # --- Perform Transformations ---
    try:
        # 2. Eliminate IFF (↔)
        ast_no_iff = eliminate_iff_ast(ast)
        # 3. Eliminate IMP (→)
        ast_no_imp = eliminate_imp_ast(ast_no_iff)
        # 4. Move Negations Inwards (NNF)
        ast_nnf = move_negation_inwards_ast(ast_no_imp)
        # 5. Distribute OR over AND (repeatedly until no changes)
        prev_ast = None
        current_ast = ast_nnf
        loop_count = 0 # Safety break for potential infinite loops (shouldn't happen)
        MAX_LOOPS = 100
        while prev_ast != current_ast:
            if loop_count > MAX_LOOPS:
                 raise RecursionError("Distribution did not converge; potential infinite loop.")
            prev_ast = deepcopy(current_ast)
            current_ast = distribute_or_over_and_ast(prev_ast)
            loop_count += 1

        final_cnf_ast = current_ast

    except (TypeError, ValueError, RecursionError) as e:
         # Catch errors during transformation steps
        error_msg = f"Error during CNF transformation: {e}"
        if return_ast:
             raise type(e)(error_msg) # Re-raise specific error if AST was expected
        return error_msg


    # 6. Return final AST or its string representation
    if return_ast:
        return final_cnf_ast
    else:
        return repr(final_cnf_ast)
    

# --- Example Usage ---

if __name__ == "__main__":
    test_formulas = [
        "p",
        "¬p",
        "p ∧ q",
        "p ∨ q",
        "p → q",
        "p ↔ q",
        "¬(p ∧ q)",
        "¬(p ∨ q)",
        "a ∨ (b ∧ c)",                             # Basic distribution right
        "(a ∧ b) ∨ c",                             # Basic distribution left
        "a → (b ∧ ¬c)",
        "r ↔ (p ∨ s)",                             # Original example
        "(a ∧ b) ∨ (c ∧ d)",                       # Double distribution
        "¬(p → q)",
        "¬(p ↔ q)",
        "((a ∨ b) ∧ c) → d",
        "¬(¬p ∨ q)",
        "p ∧ ¬p",                                  # Contradiction (simplification not done)
        "p ∨ ¬p",                                  # Tautology (simplification not done)
        "p → (q → r)",
        "(p → q) → r",
        "  a  ∨   b ",                            # Extra spaces
        " ( a ) ",                                 # Extra parentheses
        #"a ^ b"                                   # Error: Invalid operator
        #"a ∨"                                     # Error: Incomplete formula
        #"a b"                                     # Error: Missing operator
    ]

    for formula_str in test_formulas:
        print(f"Original:  {formula_str}")
        cnf_result = to_cnf(formula_str)
        print(f"CNF:       {cnf_result}")
        # Optional: Re-parse to check validity (basic check)
        try:
             if "Error" not in cnf_result:
                  Parser(cnf_result).parse()
             # print("CNF Parsed OK")
        except Exception as e:
             print(f"!! Warning: Could not re-parse generated CNF: {e}")
        print("-" * 30)

    # Example from Course
    formula = "r ↔ (p ∨ s)"
    print(f"Lecture example: {formula}")
    print(f"CNF:      {to_cnf(formula)}")
    print("-" * 30)

    # Test case requiring recursive distribution
    formula = "(a ∧ b) ∨ (c ∧ d)"
    print(f"Original:  {formula}")
    print(f"CNF:       {to_cnf(formula)}")
    print("-" * 30)

    # Test NNF carefully
    formula = "¬(a → ¬b)"
    print(f"Original:  {formula}")
    print(f"CNF:       {to_cnf(formula)}")
    print("-" * 30)
