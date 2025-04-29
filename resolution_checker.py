from typing import List, Set, Tuple

class ResolutionChecker:
    """
    Class that implements resolution-based logical entailment checking.
    """
    
    @staticmethod 
    def resolve(clause1: Set[str], clause2: Set[str]) -> List[Set[str]]:
        """
        Apply resolution rule to two clauses and return all possible resolvents (new clauses).
        A resolvent is formed by resolving a pair of complementary literals from the two clauses.
        """
        resolvents = []
        
        # Check each literal in the first clause against the second clause
        for literal in clause1:
            # The complementary literal is the same literal but of "opposite negation"
            
            if literal.startswith('¬'):
                complementary = literal[1:]  # Remove negation
            else:
                complementary = '¬' + literal  # Add negation
            
            # If the complementary literal is in the second clause, we can resolve (remove both)
            if complementary in clause2:
                # Create a new clause by merging both clauses and removing the resolved literals
                resolvent = (clause1.union(clause2) - {literal, complementary})
                
                # Avoid adding trivial clauses (tautologies like P ∨ ¬P)
                is_tautology = False
                for lit in resolvent:
                    # Check if the resolvent contains both a literal and its negation
                    if (lit.startswith('¬') and lit[1:] in resolvent) or ('¬' + lit in resolvent):
                        is_tautology = True
                        break
                
                if not is_tautology:
                    resolvents.append(resolvent) # Add the new resolvent to the list
        
        return resolvents
    
    @staticmethod
    def resolution(clauses: List[Set[str]]) -> bool:
        """
        Apply resolution repeatedly until either:
            1. An empty clause is derived (meaning the clauses are unsatisfiable)
            2. No new clauses can be derived (meaning the clauses are satisfiable)
        
        Returns:
            - True if the clauses are unsatisfiable;
            - False otherwise.
        """


        # Convert each clause to a frozenset for immutability and set operations
        # It allows me to use set operations to check for new resolvents
        # and to avoid duplicates in the clause set.
        new_clauses = set(frozenset(clause) for clause in clauses)
        
        while True:
            new_resolvents = []
            
            # Convert to list for iteration
            clause_list = list(new_clauses)
            #print(f"Current clauses: {clause_list}")

            # Try to resolve each pair of clauses
            for i in range(len(clause_list)):
                for j in range(i + 1, len(clause_list)):
                    clause1 = set(clause_list[i])
                    clause2 = set(clause_list[j])
                    
                    resolvents = ResolutionChecker.resolve(clause1, clause2)
                    
                    print(f"Resolving {clause1} and {clause2} gives: {resolvents}")

                    # Check if any resolvent is the empty clause
                    for resolvent in resolvents:
                        if len(resolvent) == 0:
                            return True  # Unsatisfiable
                        # Add non-empty resolvents to the new resolvents list
                        new_resolvents.append(resolvent)
            
            # Convert new resolvents to frozensets for set operations
            new_resolvents_set = {frozenset(r) for r in new_resolvents}
            
            # If no new clauses were derived, we're done
            if new_resolvents_set.issubset(new_clauses):
                return False  # Satisfiable
            
            # Add new resolvents to our clause set
            new_clauses.update(new_resolvents_set)

if __name__ == "__main__":
    # Test the resolve method with the following example:
    # Clause 1: {P, Q}      (meaning P ∨ Q)
    # Clause 2: {¬P, R}     (meaning ¬P ∨ R)
    # The complementary literals are P and ¬P, so they can be resolved
    # Expected result: {Q, R}   (meaning Q ∨ R)
    
    clause1 = {"P", "Q"}
    clause2 = {"¬P", "R"}
    
    print(f"Clause 1: {clause1}")
    print(f"Clause 2: {clause2}")
    
    resolvents = ResolutionChecker.resolve(clause1, clause2)
    print(f"Resolvents: {resolvents}")

    # Test the resolution function
    # We consider the entailment: (P ∧ (P → Q)) ⊨ Q
    # To check this, we convert to CNF and negate the conclusion:
    # 1. P                  (first premise)
    # 2. P → Q              (second premise, equivalent to ¬P ∨ Q)
    # 3. ¬Q                 (negation of conclusion)
    # So our clauses are: {P}, {¬P, Q}, {¬Q}
    # If resolution returns True, it means the clauses are unsatisfiable,
    # which proves that the original entailment is valid.
    
    print("\nExample 2: Testing resolution() method")
    print("Checking if (P ∧ (P → Q)) ⊨ Q")
    
    clauses = [{"P"}, {"¬P", "Q"}, {"¬Q"}]
    print(f"Clauses: {clauses}")
    
    result = ResolutionChecker.resolution(clauses)
    print(f"Resolution result (is unsatisfiable): {result}")
    
    if result:
        print("The entailment (P ∧ (P → Q)) ⊨ Q is valid.")
    else:
        print("The entailment is not valid.")
        