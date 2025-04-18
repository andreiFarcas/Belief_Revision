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


# Example usage
if __name__ == "__main__":
    # Create a belief base and add some formulas
    bb = BeliefBase()

    # Add some formulas to the belief base
    bb.add_formula("P")
    bb.add_formula("¬Q ∨ R")
    
    # Print the belief base contents
    print("Belief base:", bb.list_formulas())
    
    # Remove a formula and check the contents again
    bb.remove_formula("P")
    print("After removal:", bb.list_formulas())