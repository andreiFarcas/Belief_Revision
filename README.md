# Belief Revision

This project implements a belief base for propositional logic, supporting belief revision operations such as expansion, contraction, and entailment checking. It uses Conjunctive Normal Form (CNF) conversion and resolution-based reasoning.

## Features

- Add, remove, and list propositional formulas in a belief base
- Check logical entailment using resolution
- Convert formulas to CNF (string-based and AST-based implementations)
- Support for belief base contraction and expansion

## Files

- `belief_base.py` — Main belief base class and logic
- `cnf_converter.py` — String-based CNF conversion utilities
- `cnf_converter_ast.py` — AST-based CNF conversion utilities
- `resolution_checker.py` — Resolution algorithm for entailment checking

## Usage

1. Add formulas to the belief base (as strings, e.g., `"P → Q"`).
2. Use the `entails()` method to check if a formula is entailed.
3. Use `expansion()` and `contraction()` for belief revision.

Example: see `belief_base.py` for example usage of the functions

## Requirements

- Python 3.8+

No external dependencies are required.

## License

MIT License
