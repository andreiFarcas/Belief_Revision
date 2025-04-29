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

    def expansion(self, formula: str, priority: int = 0):
        """
        AGM Expansion: simply add the new formula.
        """
        self.add_formula(formula, priority)
        return self.list_formulas()

    def contraction(self, formula: str):
        """
        AGM Contraction: remove formula based on priority order (least important beliefs first).

        Strategy:
        - Find all beliefs that help imply the formula.
        - Prefer removing formulas with lower priority (less entrenched).
        - Minimal removal: remove as few as needed.
        """
        # Step 1: Sort formulas by priority (low priority first)
        self.formulas.sort(key=lambda x: x[1])

        # Step 2: Check if formula is implied (mocked for now, could use full entailment check)
        if not any(f == formula for (f, _) in self.formulas):
            # If formula not present, vacuity applies
            return self.list_formulas()

        # Step 3: Remove formulas that support formula (lowest priority first)
        for f, _ in self.formulas:
            if f == formula:
                self.remove_formula(f)
                break  # Only remove what is necessary

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

def test_belief_base():
    print("🔵 Creating belief base...")
    bb = BeliefBase()

    # Add initial formulas
    bb.add_formula("P")
    bb.add_formula("Q")
    bb.add_formula("R")

    print("\n✅ Initial Belief Base:")
    print(bb.list_formulas())

    # Expansion test
    print("\n🟢 Expanding with formula 'S'...")
    bb.expansion("S")
    print("Belief base after expansion:")
    print(bb.list_formulas())

    # Contraction test
    print("\n🟠 Contracting belief base on 'Q'...")
    bb.contraction("Q")
    print("Belief base after contraction:")
    print(bb.list_formulas())

    # Contraction test with a formula not present
    print("\n🟠 Contracting belief base on non-existent formula 'T'...")
    bb.contraction("T")
    print("Belief base after contraction attempt (should be no change):")
    print(bb.list_formulas())

if __name__ == "__main__":
    test_belief_base()
