# Conjunctive Normal Form (CNF) Converter
# This module converts a propositional logic formula into its CNF equivalent.

"""
    Strange symbols that we use and I don't have on my keyboard:
    ∧: AND (conjunction)
    ∨: OR (disjunction)
    ¬: NOT (negation)
    ↔: IFF (if and only if)
    →: IMP (implication)
"""

def negate_formula(formula: str) -> str:
    """
    Negates a formula by replacing:
        A with ¬A
        (A ∧ B) with ¬(A ∧ B)
        (A ∨ B) with ¬(A ∨ B)
    """
    if formula.startswith('¬'):
        # If already negated, remove the negation
        return formula[1:]
    elif formula.startswith('(') and formula.endswith(')'):
        # If the formula is parenthesized, negate the entire expression
        return f"¬({formula[1:-1]})"
    else:
        return f"¬{formula}"

def find_expression_start(formula: str) -> int:
    """Finds the starting index of the expression to the left of our operator"""
    
    balance = 0
    
    for i in range(len(formula)-1, -1, -1):
        if formula[i] == ')':
            balance += 1
        elif formula[i] == '(':
            if balance == 0:
                return i + 1
            balance -= 1
        elif balance == 0 and formula[i] in "∧∨→↔¬":
            return i + 1
    return 0

def find_expression_end(formula: str) -> int:
    """Finds the ending index of the expression to the right of our operator"""

    balance = 0
    for i in range(len(formula)):
        if formula[i] == '(':
            balance += 1
        elif formula[i] == ')':
            if balance == 0:
                return i - 1
            balance -= 1
        elif balance == 0 and i > 0 and formula[i] in "∧∨→↔":
            return i - 1
    return len(formula) - 1

# --- CNF Conversion Pipeline ---
def eliminate_iff(formula: str) -> str:
    """
    Step 1: Eliminates iff: ↔ 
    
    Replaces:
        A ↔ B with (A → B) ∧ (B → A)
    """

    i = 0
    result = ""
    while i < len(formula):
        # Checks if next character is ↔ and apply the transformation
        if i + 1 < len(formula) and formula[i:i+1] == "↔":
            # Find the beginning of the expression to the left of ↔
            left_start = find_expression_start(formula[:i-1])
            left_expr = formula[left_start:i]
            
            # Find the end of the expression to the right of ↔
            right_end = find_expression_end(formula[i+1:]) + i + 1
            right_expr = formula[i+1:right_end+1]
            
            # Replace A ↔ B with (A → B) ∧ (B → A)
            replacement = f"(({left_expr} → {right_expr}) ∧ ({right_expr} → {left_expr}))"
            
            # Remove the left_expr from the result to avoid duplication
            result = result[:-len(left_expr)]
            
            # Add the replacement
            result += replacement
            i = right_end + 1
        else:
            result += formula[i]
            i += 1

    return result

def eliminate_imp(formula: str) -> str:
    """
    Step 2: Eliminates implication: →
    
    Replaces:
        A → B with ¬A ∨ B
    """
    i = 0
    result = ""
    while i < len(formula):
        # Checks if current character is → and apply the transformation
        if i < len(formula) and formula[i:i+1] == "→":
            # Find expressions on both sides of →
            left_start = find_expression_start(formula[:i-1])
            left_expr = formula[left_start:i]
            left_expr = left_expr.strip()
            
            right_end = find_expression_end(formula[i+1:]) + i + 1
            right_expr = formula[i+1:right_end+1]
            
            result = result[:-(len(left_expr)+1)]
            
            # Replace A → B with ¬A ∨ B
            # The negation only applies to left_expr
            replacement = f"(¬{left_expr} ∨ {right_expr})"
            result += replacement
            
            i = right_end + 1
        else:
            result += formula[i]
            i += 1

    return result

def push_negations_inwards(formula: str) -> str:
    """
    Step 3: Move negations inward (Negation Normal Form)
    
    Applies:
    1. Double negation: ¬¬A = A
    2. De Morgan's laws: 
       - ¬(A ∧ B) = ¬A ∨ ¬B
       - ¬(A ∨ B) = ¬A ∧ ¬B
    """
    i = 0
    result = ""
    while i < len(formula):
        # Check for negation operator
        if formula[i] == '¬':
            # Skip the negation symbol
            i += 1
            
            # If next character is a space, skip it
            if i < len(formula) and formula[i] == ' ':
                i += 1
                
            # Check for double negation: ¬¬A = A
            if i < len(formula) and formula[i] == '¬':
                # Skip the second negation
                i += 1
                
                # Skip space if present
                if i < len(formula) and formula[i] == ' ':
                    i += 1
                    
                # Find the expression being double-negated
                if i < len(formula) and formula[i] == '(':
                    # It's a parenthesized expression
                    expr_end = find_expression_end(formula[i:]) + i
                    expr = formula[i:expr_end+1]
                    result += expr  # Add without negations
                    i = expr_end + 1
                else:
                    # It's a simple symbol
                    result += formula[i]
                    i += 1
                    
            # Check for De Morgan's laws: ¬(A ∧ B) = ¬A ∨ ¬B or ¬(A ∨ B) = ¬A ∧ ¬B
            elif i < len(formula) and formula[i] == '(':
                # Find the entire expression inside parentheses
                expr_end = find_expression_end(formula[i:]) + i
                expr = formula[i+1:expr_end]  # Remove outer parentheses
                
                # Check if this is a conjunction or disjunction
                if '∧' in expr:
                    # Apply De Morgan: ¬(A ∧ B) = ¬A ∨ ¬B
                    sub_expressions = expr.split('∧')
                    negated_expr = []
                    for sub_expr in sub_expressions:
                        sub_expr = sub_expr.strip()
                        negated_expr.append(f"¬{sub_expr}")
                    result += f"({' ∨ '.join(negated_expr)})"
                    
                elif '∨' in expr:
                    # Apply De Morgan: ¬(A ∨ B) = ¬A ∧ ¬B
                    sub_expressions = expr.split('∨')
                    negated_expr = []
                    for sub_expr in sub_expressions:
                        sub_expr = sub_expr.strip()
                        negated_expr.append(f"¬{sub_expr}")
                    result += f"({' ∧ '.join(negated_expr)})"
                    
                else:
                    # No conjunction or disjunction, just add the negation
                    result += f"¬({expr})"
                
                i = expr_end + 1
                
            else:
                # Simple negation of a variable or other expression
                result += f"¬{formula[i]}"
                i += 1
        else:
            result += formula[i]
            i += 1
            
    return result

def distribute_or(formula: str) -> str:
    """
    Step 4: Distribute ∨ over ∧ to achieve CNF
    
    Applies the distributive property:
        (A ∨ (B ∧ C)) = ((A ∨ B) ∧ (A ∨ C))
        ((A ∧ B) ∨ C) = ((A ∨ C) ∧ (B ∨ C))
    """
    # TODO: Implement the distribution of OR over AND
    pass

def normalize_spacing(formula: str) -> str:
    """
    Normalizes spacing in a formula by:
    1. Removing duplicate spaces
    2. Ensuring exactly one space before and after operation symbols
    3. Removing spaces before and after parentheses
    
    Operation symbols: ∧, ∨, ¬, ↔, →
    """
    # Define logical operators
    operators = ["∧", "∨", "¬", "↔", "→"]
    
    # Add a single space before and after each operator
    for op in operators:
        # Replace operator with space+operator+space
        formula = formula.replace(op, f" {op} ")
    
    # Remove spaces before and after parentheses
    formula = formula.replace("( ", "(").replace(" )", ")")
    
    # Simply find multiple spaces and replace them by a single space
    while "  " in formula:
        formula = formula.replace("  ", " ")
    
    # Trim spaces at the beginning and end
    formula = formula.strip()
    
    return formula

def normalize_parentheses(formula: str) -> str:
    """
    Normalizes parentheses in a formula by:
    1. Removing redundant nested parentheses around atomic propositions
    2. Removing redundant outer parentheses from the whole formula
    3. Preserving parentheses that are needed for proper operator precedence
    
    Examples:
    - ((a)) becomes (a)
    - (a) becomes a (when not part of a larger expression)
    - Preserves parentheses for complex expressions
    """
    # Use a stack-based approach for parentheses balancing
    def simplify_expr(expr: str) -> str:
        # Base case: single letter/symbol or empty string
        expr = expr.strip()
        if len(expr) <= 1:
            return expr
            
        # Check if expression is surrounded by unnecessary parentheses
        if expr[0] == '(' and expr[-1] == ')':
            # Ensure these are matching parentheses, not part of separate sub-expressions
            balance = 0
            for i in range(len(expr) - 1):  # Exclude the last char
                if expr[i] == '(':
                    balance += 1
                elif expr[i] == ')':
                    balance -= 1
                # If balance goes to 0 before the end, the outer parens aren't a matching pair
                if balance == 0 and i < len(expr) - 1:
                    break
            else:  # No break occurred - the outer parentheses match
                # Recursively simplify the inner expression
                inner = simplify_expr(expr[1:-1])
                
                # If inner is a simple symbol or already balanced expression
                if (len(inner) == 1 or 
                    ('∧' not in inner and '∨' not in inner and '¬' not in inner and '→' not in inner and '↔' not in inner)):
                    return inner
                
                # If the inner part has operators, keep the parentheses
                return f"({inner})"
        
        # If expression contains operators, process parts around them
        for op in ['∧', '∨', '→', '↔']:
            if op in expr:
                # Don't split inside parenthesized sub-expressions
                balance = 0
                parts = []
                last_idx = 0
                
                for i, char in enumerate(expr):
                    if char == '(':
                        balance += 1
                    elif char == ')':
                        balance -= 1
                    elif balance == 0 and char == op:
                        parts.append(expr[last_idx:i])
                        last_idx = i + 1
                
                if parts:
                    parts.append(expr[last_idx:])
                    simplified_parts = [simplify_expr(part) for part in parts]
                    return op.join(simplified_parts)
        
        # Handle negation specially
        if expr.startswith('¬'):
            inner = simplify_expr(expr[1:])
            return f"¬{inner}"
            
        return expr
    
    # Initial simplification
    simplified = simplify_expr(formula)
    
    # Ensure we don't have extra spaces around parentheses
    simplified = simplified.replace('( ', '(').replace(' )', ')')
    
    return simplified

def cnf_to_clauses(formula: str) -> list:
    """
    Converts a CNF formula into a list of clauses.
    
    Each clause is represented as a set of literals.
    """
    # Split the formula by conjunctions
    clauses = formula.split('∧')
    
    # Convert each clause into a set of literals with spaces removed
    return [set(literal.strip() for literal in clause.strip().split('∨')) for clause in clauses]

if __name__ == "__main__":
    # Testing the CNF conversion 
    formula = "r ↔ (p ∨ s)"
    print("Original formula:", normalize_spacing(formula))

    # Step 1: Eliminate IFF (↔)
    formula_no_iff = eliminate_iff(formula)
    formula_no_iff = normalize_parentheses(formula_no_iff)
    formula_no_iff = normalize_spacing(formula_no_iff)
    
    print("After eliminating IFF:", formula_no_iff)

    # Step 2: Eliminate IMP (→)
    formula_no_imp = eliminate_imp(formula_no_iff)
    formula_no_imp = normalize_parentheses(formula_no_imp)
    formula_no_imp = normalize_spacing(formula_no_imp)

    print("After eliminating IMP:", formula_no_imp)
    
    # Step 3: Push negations inwards
    formula_nnf = push_negations_inwards(formula_no_imp)
    formula_nnf = normalize_parentheses(formula_nnf)
    formula_nnf = normalize_spacing(formula_nnf)

    print("After pushing negations inwards:", formula_nnf)

    #Step 4: Distribute OR over AND
    # formula_cnf = distribute_or(formula_nnf)
    # formula_cnf = normalize_spacing(formula_cnf)
    # formula_cnf = normalize_parentheses(formula_cnf)
    # print("After distributing the OR:", formula_cnf)

    # Testing the CNF to clauses conversion
    # Assuming the formula is already in CNF
    cnf_formula = "P ∨ Q ∧ R ∨ S"
    print("CNF formula:", cnf_formula)
    clauses = cnf_to_clauses(cnf_formula)
    print("Clauses:", clauses)
