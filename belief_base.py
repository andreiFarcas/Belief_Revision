from resolution_checker import ResolutionChecker
from cnf_converter import negate_formula, cnf_to_clauses

class BeliefBase:
    """
    A belief base storing propositional formulas as strings.
    Provides operations to add, remove, check, and list formulas.
    """
    def __init__(self):
        """Initialize an empty belief base with prioritized formulas."""
        self.formulas = []  # List of tuples (formula, priority)

    def add_formula(self, formula: str, priority: int = 1):
        """
        Add a formula to the belief base if not already present.
        Formulas must be provided as strings.
        """
        if not self.contains(formula):
            self.formulas.append((formula, priority))

    def remove_formula(self, formula: str):
        """Remove a formula from the belief base if it exists."""
        self.formulas = [(f, p) for f, p in self.formulas if f != formula]

    def empty(self) -> None:
        """
        Empty the belief base by removing all formulas.
        """
        self.formulas = []
        print("Belief base emptied.")

    def contains(self, formula: str) -> bool:
        """
        Check if a formula is present in the belief base.
        Returns True if the formula is found, False otherwise.
        """
        return any(f == formula for f, _ in self.formulas)
    
    def list_formulas(self) -> list:
        """
        Returns a copy of the list of formulas in the belief base.
        """
        return [f for f, _ in self.formulas]
    
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
        for formula, _ in self.formulas:  # Unpack the tuple here
            cnf_formula = cnf_to_clauses(formula)
            cnf_clauses.extend(cnf_formula)

        print("Belief base:", self.list_formulas())
        print("CNF Clauses:", cnf_clauses)

        # Combine the belief base clauses with the negated formula clauses
        cnf_clauses.extend(negated_cnf_entailed_clauses)

        print("Final CNF Clauses with negated formula included:", cnf_clauses)

        # Apply resolution; if unsatisfiable, then the belief base entails the formula
        return ResolutionChecker.resolution(cnf_clauses)
    
    def expansion(self, formula: str, priority: int = 1) -> bool:
        """
        Expand the belief base with a new formula.
        
        Args:
            formula: The formula to add
            priority: Priority of the formula (default=1)
            
        Returns:
            bool: True if expansion was successful, False if formula was already present
        """
        # Check if formula is already present
        if self.contains(formula):
            print(f"Formula '{formula}' is already in the belief base.")
            return False
            
        # Add the new formula
        self.formulas.append((formula, priority))
        print(f"Added '{formula}' with priority {priority}")
        return True

# Example usage
#if __name__ == "__main__":
    # Create a belief base
#    bb = BeliefBase()
    
    # Test expansion
 #   print("\n=== Testing Expansion ===")
  #  bb.expansion("P", priority=2)
   # bb.expansion("P → Q", priority=1)
    #print(f"Current beliefs: {bb.list_formulas()}")
    
    # Test entailment after expansion
  #  print("\n=== Testing Entailment ===")
  #  result = bb.entails("Q")
  #  print(f"P, P→Q entails Q? {result}")
    
    # Test duplicate expansion
  #  print("\n=== Testing Duplicate Expansion ===")
  #  result = bb.expansion("P", priority=3)
  #  print(f"Expansion successful? {result}")
  #  print(f"Final beliefs: {bb.list_formulas()}"))


if __name__ == "__main__":
    # Create a belief base and add some formulas
    bb = BeliefBase()

    # Empty the belief base
    bb.empty()
    print("After emptying:", bb.list_formulas())  # Should print: []

    # Add some formulas to the belief base
    bb.add_formula("¬P ∨ Q", priority=2)
    bb.add_formula("P", priority=1)

    # Test expansion
    bb.expansion("X", priority=2)
    bb.expansion("P → Q", priority=1)
    
    # Check if the belief base entails a formula    
    # Extracting the clauses from the belief base for entailment checking
    entails_result = bb.entails("Q")
    print("Entails Q:", entails_result)

    entails_result = bb.entails("¬R")
    print("Entails ¬R:", entails_result)

