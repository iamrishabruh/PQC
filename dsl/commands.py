# dsl/commands.py

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator
import random

class Commands:
    def __init__(self):
        # Initialize Quantum and Classical Registers
        self.qreg = QuantumRegister(0)
        self.creg = ClassicalRegister(0)
        self.circuit = QuantumCircuit()

        # Dictionaries to keep track of qubits and classical bits
        self.qubits = {}
        self.classical_bits = {}

        # Instruction queue for print commands
        self.instructions = []

        # Lists to store Alice's and Bob's bits and bases
        self.alice_bits = []
        self.alice_bases = []
        self.bob_bases = []
        self.bob_bits = []

        # Shared key after sifting
        self.shared_key = []

        # Eavesdropping flag and probability
        self.eavesdropping = False
        self.eavesdrop_probability = 0.5  # Default 50%

        # Error rate threshold for eavesdropping detection
        self.error_threshold = 0.1  # Default 10%

        # Initialize the AerSimulator backend
        self.simulator = AerSimulator()

    def define_qubit(self, q_name):
        if q_name in self.qubits:
            raise ValueError(f"Qubit '{q_name}' is already defined.")

        # Add a new qubit to the Quantum Register
        self.qreg = QuantumRegister(1, q_name)
        self.circuit.add_register(self.qreg)
        self.qubits[q_name] = self.qreg[0]
        print(f"Defined qubit '{q_name}'.")

    def apply_gate(self, gate, q_name, target_q=None):
        if gate in ["h", "x"]:
            if q_name not in self.qubits:
                raise ValueError(f"Qubit '{q_name}' is not defined.")
            if gate == "h":
                self.circuit.h(self.qubits[q_name])
                print(f"Applied Hadamard gate on '{q_name}'.")
            elif gate == "x":
                self.circuit.x(self.qubits[q_name])
                print(f"Applied Pauli-X gate on '{q_name}'.")
        elif gate == "cnot":
            if q_name not in self.qubits:
                raise ValueError(f"Control qubit '{q_name}' is not defined.")
            if target_q not in self.qubits:
                raise ValueError(f"Target qubit '{target_q}' is not defined.")
            self.circuit.cx(self.qubits[q_name], self.qubits[target_q])
            print(f"Applied CNOT gate with control '{q_name}' and target '{target_q}'.")
        else:
            raise ValueError(f"Unknown gate '{gate}'.")

    def measure_qubit(self, q_name, c_name):
        if q_name not in self.qubits:
            raise ValueError(f"Qubit '{q_name}' is not defined.")
        if c_name in self.classical_bits:
            raise ValueError(f"Classical bit '{c_name}' is already defined.")

        # Add a new classical bit
        self.creg = ClassicalRegister(1, c_name)
        self.circuit.add_register(self.creg)
        self.classical_bits[c_name] = self.creg[0]

        # Measure the qubit into the classical bit
        self.circuit.measure(self.qubits[q_name], self.classical_bits[c_name])
        print(f"Measured qubit '{q_name}' into classical bit '{c_name}'.")

    def print_variable(self, var_name):
        # Schedule the variable for printing after execution
        self.instructions.append(("print", var_name))
        print(f"Scheduled print for variable '{var_name}'.")

    def alice_send_qubit(self, q_name):
        if q_name not in self.qubits:
            raise ValueError(f"Qubit '{q_name}' is not defined.")

        # Alice randomly selects a bit (0 or 1) and a basis (0: Rectilinear '+', 1: Diagonal 'x')
        bit = random.randint(0, 1)
        basis = random.randint(0, 1)

        self.alice_bits.append(bit)
        self.alice_bases.append(basis)

        # Prepare the qubit based on the selected basis and bit
        if basis == 0:
            # Rectilinear basis
            if bit == 1:
                self.circuit.x(self.qubits[q_name])
        else:
            # Diagonal basis
            self.circuit.h(self.qubits[q_name])
            if bit == 1:
                self.circuit.x(self.qubits[q_name])

        # Add a barrier to separate operations
        self.circuit.barrier()

        print(
            f"Alice sent qubit '{q_name}' with bit={bit} and basis={'+' if basis == 0 else 'x'}."
        )

    def bob_measure_qubit(self, q_name, basis_str):
        if q_name not in self.qubits:
            raise ValueError(f"Qubit '{q_name}' is not defined.")

        # Map basis string to integer
        if basis_str.upper() == "H":
            basis = 0  # Rectilinear
        elif basis_str.upper() == "X":
            basis = 1  # Diagonal
        else:
            raise ValueError(
                f"Invalid basis '{basis_str}'. Use 'H' for rectilinear or 'X' for diagonal."
            )

        self.bob_bases.append(basis)

        # Apply basis transformation if necessary
        if basis == 1:
            self.circuit.h(self.qubits[q_name])

        # Define a classical bit name based on qubit name
        c_name = f"c_{q_name}"
        if c_name in self.classical_bits:
            raise ValueError(f"Classical bit '{c_name}' is already defined.")

        # Add a new classical bit and measure
        self.creg = ClassicalRegister(1, c_name)
        self.circuit.add_register(self.creg)
        self.classical_bits[c_name] = self.creg[0]
        self.circuit.measure(self.qubits[q_name], self.classical_bits[c_name])

        print(
            f"Bob measured qubit '{q_name}' with basis={'+' if basis == 0 else 'x'} into classical bit '{c_name}'."
        )

    def sift_keys(self):
        # Transpile the circuit for the AerSimulator backend
        compiled_circuit = transpile(self.circuit, self.simulator)

        # Execute the transpiled circuit on the AerSimulator
        job = self.simulator.run(compiled_circuit, shots=1)
        result = job.result()
        counts = result.get_counts()
        outcome = list(counts.keys())[0]

        print(f"Measurement outcome: {outcome}")

        # Extract Bob's bits based on classical bits
        for q_name in self.qubits:
            c_name = f"c_{q_name}"
            if c_name in self.classical_bits:
                # Qiskit returns bitstrings in little endian; reverse the outcome
                bit_index = list(self.classical_bits.keys()).index(c_name)
                bit = int(outcome[::-1][bit_index])
                self.bob_bits.append(bit)

        # Sift keys where Alice's and Bob's bases match
        for i in range(len(self.alice_bases)):
            if self.alice_bases[i] == self.bob_bases[i]:
                self.shared_key.append(self.alice_bits[i])

        print(f"Sifted key: {self.shared_key}")

    def check_eavesdropping(self, probability=0.5, threshold=0.1):
        # Update eavesdropping parameters if provided
        self.eavesdrop_probability = probability
        self.error_threshold = threshold

        print("Checking for eavesdropping...")

        # Simulate eavesdropping based on the specified probability
        if self.eavesdropping:
            # Insert logic for eavesdropping check if implemented
            pass  # Placeholder for future implementation

        # Placeholder: In this basic implementation, assume no eavesdropping
        error_rate = 0  # To be calculated based on actual measurements

        if error_rate > self.error_threshold:
            print("Eavesdropping detected!")
        else:
            print("No eavesdropping detected.")

    def generate_key(self, key_name):
        if not self.shared_key:
            raise ValueError("No shared key available to generate.")

        # Concatenate sifted bits into a binary string
        key = "".join(str(bit) for bit in self.shared_key)

        # Assign the key to the specified key name
        setattr(self, key_name, key)

        print(f"Generated key '{key_name}': {key}")

    def execute_eavesdropping(self, custom_probability=None):
        # Simulate Eve intercepting and measuring qubits based on probability
        if custom_probability is not None:
            self.eavesdrop_probability = custom_probability
        else:
            self.eavesdrop_probability = 0.5  # Default 50%

        print(
            f"Eavesdropping simulation initiated with probability {self.eavesdrop_probability*100}%."
        )

        for q_name in self.qubits:
            if random.random() < self.eavesdrop_probability:
                # Eve chooses a random basis
                basis = random.randint(0, 1)
                basis_str = "H" if basis == 0 else "X"
                print(
                    f"Eve intercepts qubit '{q_name}' and measures with basis '{basis_str}'."
                )

                # Apply basis transformation if diagonal
                if basis == 1:
                    self.circuit.h(self.qubits[q_name])

                # Define a classical bit name for Eve's measurement
                c_name = f"c_eve_{q_name}"
                if c_name in self.classical_bits:
                    raise ValueError(f"Classical bit '{c_name}' is already defined.")

                # Add a new classical bit and measure
                self.creg = ClassicalRegister(1, c_name)
                self.circuit.add_register(self.creg)
                self.classical_bits[c_name] = self.creg[0]
                self.circuit.measure(self.qubits[q_name], self.classical_bits[c_name])

                print(
                    f"Eve measured qubit '{q_name}' and stored the result in classical bit '{c_name}'."
                )
