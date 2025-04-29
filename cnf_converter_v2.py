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

# --- Formula Negation ---
def negate_formula(formula: str) -> str:
    """
    Negates a formula by replacing:
        A with ¬A
        (A ∧ B) with ¬(A ∧ B)
        (A ∨ B) with ¬(A ∨ B)
    """
    if formula.startswith('¬'):
        return formula[1:]
    elif formula.startswith('(') and formula.endswith(')'):
        return f"¬({formula[1:-1]})"
    else:
        return f"¬{formula}"

# --- Helper Functions to Find Expression Parts ---
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
    Step 1: Eliminates IFF (↔)
    
    Replaces:
        A ↔ B with (A → B) ∧ (B → A)
    """
    i = 0
    result = ""
    while i < len(formula):
        if i + 1 < len(formula) and formula[i:i+1] == "↔":
            left_start = find_expression_start(formula[:i-1])
            left_expr = formula[left_start:i]
            right_end = find_expression_end(formula[i+1:]) + i + 1
            right_expr = formula[i+1:right_end+1]
            replacement = f"(({left_expr} → {right_expr}) ∧ ({right_expr} → {left_expr}))"
            result = result[:-len(left_expr)]
            result += replacement
            i = right_end + 1
        else:
            result += formula[i]
            i += 1
    return result

def eliminate_imp(formula: str) -> str:
    """
    Step 2: Eliminates implication (→)
    
    Replaces:
        A → B with ¬A ∨ B
    """
    i = 0
    result = ""
    while i < len(formula):
        if i < len(formula) and formula[i:i+1] == "→":
            left_start = find_expression_start(formula[:i-1])
            left_expr = formula[left_start:i].strip()
            right_end = find_expression_end(formula[i+1:]) + i + 1
            right_expr = formula[i+1:right_end+1]
            result = result[:-(len(left_expr)+1)]
            replacement = f"(¬{left_expr} ∨ {right_expr})"
            result += replacement
            i = right_end + 1
        else:
            result += formula[i]
            i += 1
    return result

def push_negations_inwards(formula: str) -> str:
    """
    Step 3: Move negations inward (Negation Normal Form - NNF)
    
    Applies:
    1. Double negation: ¬¬A = A
    2. De Morgan's laws: 
       - ¬(A ∧ B) = (¬A ∨ ¬B)
       - ¬(A ∨ B) = (¬A ∧ ¬B)
    """
    i = 0
    result = ""
    while i < len(formula):
        if formula[i] == '¬':
            i += 1
            if i < len(formula) and formula[i] == ' ':
                i += 1
            if i < len(formula) and formula[i] == '¬':
                i += 1
                if i < len(formula) and formula[i] == ' ':
                    i += 1
                if i < len(formula) and formula[i] == '(':
                    expr_end = find_expression_end(formula[i:]) + i
                    expr = formula[i:expr_end+1]
                    result += expr
                    i = expr_end + 1
                else:
                    result += formula[i]
                    i += 1
            elif i < len(formula) and formula[i] == '(':
                expr_end = find_expression_end(formula[i:]) + i
                expr = formula[i+1:expr_end]
                if '∧' in expr:
                    sub_expressions = expr.split('∧')
                    negated_expr = [f"¬{sub.strip()}" for sub in sub_expressions]
                    result += f"({' ∨ '.join(negated_expr)})"
                elif '∨' in expr:
                    sub_expressions = expr.split('∨')
                    negated_expr = [f"¬{sub.strip()}" for sub in sub_expressions]
                    result += f"({' ∧ '.join(negated_expr)})"
                else:
                    result += f"¬({expr})"
                i = expr_end + 1
            else:
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
    import re
    if '∧' not in formula:
        return formula

    pattern = r'\(([^()]+)\)'
    matches = list(re.finditer(pattern, formula))
    
    for match in matches:
        content = match.group(1)
        
        if '∨' in content:
            parts = content.split('∨')
            left = parts[0].strip()
            right = parts[1].strip()

            if '∧' in right:
                subparts = right.split('∧')
                new_formula = f"({left} ∨ {subparts[0].strip()}) ∧ ({left} ∨ {subparts[1].strip()})"
                formula = formula.replace(match.group(0), new_formula)
                return distribute_or(formula)

            elif '∧' in left:
                subparts = left.split('∧')
                new_formula = f"({subparts[0].strip()} ∨ {right}) ∧ ({subparts[1].strip()} ∨ {right})"
                formula = formula.replace(match.group(0), new_formula)
                return distribute_or(formula)

    return formula

def normalize_spacing(formula: str) -> str:
    """
    Normalizes spacing in a formula:
    1. One space before/after logical symbols
    2. No spaces inside parentheses
    """
    operators = ["∧", "∨", "¬", "↔", "→"]
    for op in operators:
        formula = formula.replace(op, f" {op} ")
    formula = formula.replace("( ", "(").replace(" )", ")")
    while "  " in formula:
        formula = formula.replace("  ", " ")
    return formula.strip()

def normalize_parentheses(formula: str) -> str:
    """
    Normalizes parentheses:
    1. Removes redundant parentheses
    2. Preserves important operator groupings
    """
    def simplify_expr(expr: str) -> str:
        expr = expr.strip()
        if len(expr) <= 1:
            return expr
        if expr[0] == '(' and expr[-1] == ')':
            balance = 0
            for i in range(len(expr) - 1):
                if expr[i] == '(':
                    balance += 1
                elif expr[i] == ')':
                    balance -= 1
                if balance == 0 and i < len(expr) - 1:
                    break
            else:
                inner = simplify_expr(expr[1:-1])
                if (len(inner) == 1 or all(op not in inner for op in ['∧', '∨', '¬', '→', '↔'])):
                    return inner
                return f"({inner})"
        for op in ['∧', '∨', '→', '↔']:
            if op in expr:
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
        if expr.startswith('¬'):
            inner = simplify_expr(expr[1:])
            return f"¬{inner}"
        return expr
    simplified = simplify_expr(formula)
    simplified = simplified.replace('( ', '(').replace(' )', ')')
    return simplified

def cnf_to_clauses(formula: str) -> list:
    """
    Converts a CNF formula string into a list of clauses (sets of literals).
    """
    clauses = formula.split('∧')
    return [set(literal.strip() for literal in clause.strip().split('∨')) for clause in clauses]

def convert_to_cnf(formula: str) -> list:
    """
    Full CNF conversion pipeline.
    Takes a propositional formula and returns list of clauses in CNF.
    """
    formula = normalize_spacing(formula)
    formula = eliminate_iff(formula)
    formula = normalize_parentheses(formula)
    formula = normalize_spacing(formula)
    formula = eliminate_imp(formula)
    formula = normalize_parentheses(formula)
    formula = normalize_spacing(formula)
    formula = push_negations_inwards(formula)
    formula = normalize_parentheses(formula)
    formula = normalize_spacing(formula)
    formula = distribute_or(formula)
    formula = normalize_spacing(formula)
    formula = normalize_parentheses(formula)
    return cnf_to_clauses(formula)

# --- Example usage ---
if __name__ == "__main__":
    formula = "P → (Q → R)"
    print("Original formula:", formula)
    clauses = convert_to_cnf(formula)
    print("CNF Clauses:", clauses)
