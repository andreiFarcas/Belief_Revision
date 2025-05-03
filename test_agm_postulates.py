from belief_base import BeliefBase

def test_success():
    print("Testing SUCCESS postulate...")
    bb = BeliefBase()
    bb.add_formula("¬P ∨ Q")
    bb.add_formula("P")
    assert bb.entails("Q"), "Q should be entailed before contraction"
    bb.contraction("Q")
    assert not bb.entails("Q"), "Q should NOT be entailed after contraction"
    print("SUCCESS postulate passed.")

def test_inclusion():
    print("Testing INCLUSION postulate...")
    bb = BeliefBase()
    bb.add_formula("¬P ∨ Q")
    bb.add_formula("P")
    before = set(bb.list_formulas())
    bb.contraction("Q")
    after = set(bb.list_formulas())
    assert after.issubset(before), "Belief base after contraction must be subset of before"
    print("INCLUSION postulate passed.")

def test_vacuity():
    print("Testing VACUITY postulate...")
    bb = BeliefBase()
    bb.add_formula("A")
    before = set(bb.list_formulas())
    bb.contraction("B")  # B is not entailed
    after = set(bb.list_formulas())
    assert before == after, "Belief base should be unchanged if formula not entailed"
    print("VACUITY postulate passed.")

def test_consistency():
    print("Testing CONSISTENCY postulate...")
    bb = BeliefBase()
    bb.add_formula("P")
    bb.add_formula("¬P ∨ Q")
    bb.contraction("Q")
    assert not bb.entails("False"), "Belief base should not entail contradiction"
    print("CONSISTENCY postulate passed.")

def test_extensionality():
    print("Testing EXTENSIONALITY postulate...")
    bb1 = BeliefBase()
    bb2 = BeliefBase()
    for f in ["P", "¬P ∨ Q"]:
        bb1.add_formula(f)
        bb2.add_formula(f)

    phi = "Q"
    psi = "¬¬Q"

    bb1.contraction(phi)
    bb2.contraction(psi)
    assert set(bb1.list_formulas()) == set(bb2.list_formulas()), "Equivalent formulas should yield identical contractions"
    print("EXTENSIONALITY postulate passed.")

if __name__ == "__main__":
    tests = [
        ("SUCCESS", test_success),
        ("INCLUSION", test_inclusion),
        ("VACUITY", test_vacuity),
        ("CONSISTENCY", test_consistency),
        ("EXTENSIONALITY", test_extensionality),
    ]

    print("Running AGM Postulate Tests...\n")
    passed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"{name} postulate FAILED: {e}")
        print("-" * 50)

    print(f"\n {passed}/{len(tests)} tests passed.")