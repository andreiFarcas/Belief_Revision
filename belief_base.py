from resolution_checker import ResolutionChecker
from cnf_converter import negate_formula, cnf_to_clauses

class BeliefBase:
    """
    A belief base storing propositional formulas as strings.
    Provides operations to add, remove, check, and list formulas.
    """
    def __init__(self):
        self.formulas = []  # Initialize an empty list of formulas

    def add_formula(self, formula: str):
        """
        Add a formula to the belief base if not already present.
        Formulas must be provided as strings.
        """
        if formula not in self.formulas:
            self.formulas.append(formula)

    def remove_formula(self, formula: str):
        """
        Remove a formula from the belief base if it exists.
        Formulas must be provided as strings.
        """
        if formula in self.formulas:
            self.formulas.remove(formula)

    def contains(self, formula: str) -> bool:
        """
        Check if a formula is present in the belief base.
        Returns True if the formula is found, False otherwise.
        """
        return formula in self.formulas

    def list_formulas(self) -> list:
        """
        Returns a copy of the list of formulas in the belief base.
        """
        return list(self.formulas)
    
    def entails(self, entailed_formula: str) -> bool:
        """
        Check if the belief base entails a given formula.

        Uses resolution-based proof by contradiction:
        - If BB ⊨ φ, then BB ∪ {¬φ} must be unsatisfiable
        
        Returns True if the formula is entailed, False otherwise.
        """
        negated_entailed_formula = negate_formula(entailed_formula)
        negated_cnf_entailed_clauses = cnf_to_clauses(negated_entailed_formula)
        print("Negated formula:", negated_cnf_entailed_clauses)
        
        cnf_clauses = []
        for formula in self.formulas:
            cnf_formula = cnf_to_clauses(formula)
            cnf_clauses.extend(cnf_formula)

        print("Belief base:", self.list_formulas())
        print("CNF Clauses:", cnf_clauses)

        # Combine the belief base clauses with the negated formula clauses
        cnf_clauses.extend(negated_cnf_entailed_clauses)

        print("Final CNF Clauses with negated formula included:", cnf_clauses)

        # Apply resolution; if unsatisfiable, then the belief base entails the formula
        return ResolutionChecker.resolution(cnf_clauses)

# Example usage
if __name__ == "__main__":
    # Create a belief base and add some formulas
    bb = BeliefBase()

    # Add some formulas to the belief base
    bb.add_formula("¬P ∨ Q")
    bb.add_formula("P")
    
    # Check if the belief base entails a formula    
    # Extracting the clauses from the belief base for entailment checking
    entails_result = bb.entails("Q")
    print("Entails Q:", entails_result)

    entails_result = bb.entails("¬R")
    print("Entails ¬R:", entails_result)