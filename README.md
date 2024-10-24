# Quantum DSL: BB84 Protocol Implementation

![License](https://img.shields.io/badge/license-MIT-blue.svg)

Quantum DSL is a domain-specific language designed to implement quantum operations, focusing on the BB84 Quantum Key Distribution (QKD) protocol. It offers an intuitive syntax for defining and executing quantum processes, abstracting the complexities of quantum mechanics.

## Features

- **BB84 Quantum Key Distribution**: Implements Alice and Bob's operations for preparing, sending, and measuring qubits, along with key sifting and generation.
- **Quantum Operations**: Supports qubit allocation, standard quantum gates (H, X, CNOT), and measurements.
- **Post-Processing for QKD**: Includes key sifting and secure key generation.
- **Utility Functions**: Assists with key management, parsing, and user interactions.
- **Extensible Design**: Easily add new quantum gates, control flows, and post-processing steps.

## Directory Structure

```
Quantum-DSL/
├── main.py           # Entry point for executing DSL scripts
├── bb84.dsl          # Sample BB84 protocol script
├── utils.py          # Utility functions
├── parser.py         # DSL grammar and tokens
├── parsetab.py       # Parser table (auto-generated)
├── parser.out        # Parser output (auto-generated)
├── interpreter.py    # Core interpreter logic
├── commands.py       # Command definitions for quantum operations
├── __init__.py       # Package initializer
├── tests/            # Unit tests
└── LICENSE
```

## Installation

### Prerequisites

- Python 3.x
- [PLY (Python Lex-Yacc)](https://github.com/dabeaz/ply)

### Install Dependencies

```bash
pip install ply
```

## Usage

### Running a DSL Script

Execute a DSL script using the following command:

```bash
python main.py path/to/your_script.dsl
```

### Example

To run the provided BB84 example:

```bash
python main.py bb84.dsl
```

## Example Script (`bb84.dsl`)

```dsl
QUBIT A
H A
ALICE_SEND A
BOB_MEASURE A B
SIFT_KEYS
GENERATE_KEY secure_key 128
```

This script allocates a qubit, applies a Hadamard gate, sends the qubit from Alice to Bob, measures it, sifts the keys, and generates a secure key.

## Extending the DSL

### Adding Quantum Gates

1. **Define the Gate**: Add the gate logic in `commands.py`.
2. **Interpretation Logic**: Implement the gate behavior in `interpreter.py`.

### Control Flow

Introduce conditionals and loops by extending the grammar in `parser.py` and handling them in `interpreter.py`.

### Post-Processing Enhancements

Implement additional QKD steps like privacy amplification and error correction within `commands.py` and `interpreter.py`.

### Improved Error Handling

Enhance validation and error messages in the parser and interpreter to provide better user feedback.

## Testing

Ensure the DSL functions correctly by running unit tests:

```bash
python -m unittest discover tests/
```

*Add your test cases in the `tests/` directory.*

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch for your feature.
3. Commit your changes and push to your fork.
4. Open a pull request for review.

*Please adhere to the coding style and include appropriate tests.*

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions or suggestions, please open an issue in the repository or contact the author at [rchouhan.network@gmail.com](mailto:rchouhan.network@gmail.com).
