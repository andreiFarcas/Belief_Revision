from resolution_checker import ResolutionChecker
from cnf_converter_v2 import negate_formula, cnf_to_clauses

class BeliefBase:
    def __init__(self):
        self.formulas = []  # List of tuples (formula, priority)

    def add_formula(self, formula: str, priority: int = 0):
        """
        Add a formula to the belief base with a given priority.
        Higher priority = more important belief.
        """
        if not any(f == formula for (f, _) in self.formulas):
            self.formulas.append((formula, priority))

    def list_formulas(self) -> list:
        """
        List all formulas without priority.
        """
        return [formula for (formula, _) in self.formulas]

    def remove_formula(self, formula: str):
        """
        Remove a formula from the belief base.
        """
        self.formulas = [(f, p) for (f, p) in self.formulas if f != formula]

    def expansion(self, formula: str, priority: int = 0):
        """
        AGM Expansion: simply add the new formula.
        """
        self.add_formula(formula, priority)
        return self.list_formulas()

    def entails(self, formulas: list, query: str) -> bool:
        """
        Helper: check entailment for a list of formulas.
        """
        negated_query = negate_formula(query)
        cnf_clauses = []
        for f in formulas:
            cnf_clauses.extend(cnf_to_clauses(f))
        cnf_clauses.extend(cnf_to_clauses(negated_query))
        return ResolutionChecker.resolution(cnf_clauses)

    def contraction(self, formula: str):
        """
        AGM Contraction: remove formula based on priority order (least important beliefs first),
        with real logical entailment check.
        """
        # Step 1: Check if contraction is necessary
        current_formulas = [f for (f, _) in self.formulas]
        if not self.entails(current_formulas, formula):
            # Vacuity: nothing to do
            return self.list_formulas()

        # Step 2: Sort by priority (lowest priority first)
        self.formulas.sort(key=lambda x: x[1])

        # Step 3: Try removing formulas until entailment is broken
        for i in range(len(self.formulas)):
            # Create a tentative new belief base without one formula
            new_base = [f for j, (f, _) in enumerate(self.formulas) if j != i]
            if not self.entails(new_base, formula):
                # If formula no longer follows, accept the removal
                removed_formula = self.formulas[i][0]
                print(f"🔴 Removing '{removed_formula}' to contract '{formula}'")
                self.formulas = [(f, p) for (f, p) in self.formulas if f != removed_formula]
                return self.list_formulas()

        # If we tried everything and still entail the formula, fallback
        print(f"⚠️ Warning: Could not fully contract '{formula}'. Returning minimal base.")
        return self.list_formulas()

if __name__ == "__main__":
    # Example usage
    bb = BeliefBase()

    bb.add_formula("P", priority=2)
    bb.add_formula("P → Q", priority=3)
    bb.add_formula("Q", priority=1)

    print("Initial Belief Base:", bb.list_formulas())

    print("\n--- Expansion ---")
    bb.expansion("R", priority=2)
    print("After expansion:", bb.list_formulas())

    print("\n--- Contraction ---")
    bb.contraction("Q")
    print("After contraction:", bb.list_formulas())


if __name__ == "__main__":
    bb = BeliefBase()

    bb.add_formula("P", priority=5)
    bb.add_formula("P → Q", priority=4)
    bb.add_formula("Q → R", priority=3)
    bb.add_formula("R → S", priority=2)
    bb.add_formula("S → T", priority=1)
    bb.add_formula("U", priority=2)

    print("🧩 Initial Belief Base:", bb.list_formulas())

    print("\n--- Expansion (adding nothing for now) ---")
    # No expansion for this example

    print("\n--- Contraction: Trying to contract 'R' ---")
    bb.contraction("R")
    print("📚 Belief Base after contraction:", bb.list_formulas())