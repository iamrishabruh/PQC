from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Commands:
    def __init__(self):
        # Initialize Quantum and Classical Registers
        self.qreg_counter = 0
        self.creg_counter = 0
        self.qreg = QuantumRegister(0, 'qreg')
        self.creg = ClassicalRegister(0, 'creg')
        self.circuit = QuantumCircuit()
        self.circuit.add_register(self.qreg)
        self.circuit.add_register(self.creg)

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

        # Create a new QuantumRegister with a unique name
        qreg_name = f'qreg_{self.qreg_counter}'
        qreg = QuantumRegister(1, qreg_name)
        self.circuit.add_register(qreg)
        self.qubits[q_name] = qreg[0]  # Store the actual qubit reference
        logger.info(f"Defined qubit '{q_name}'.")

        # Create a corresponding ClassicalRegister with a unique name
        creg_name = f'creg_{self.creg_counter}'
        creg = ClassicalRegister(1, creg_name)
        self.circuit.add_register(creg)
        self.classical_bits[f'c_{q_name}'] = creg[0]
        logger.info(f"Defined classical bit 'c_{q_name}' for qubit '{q_name}'.")

        # Increment counters for unique register naming
        self.qreg_counter += 1
        self.creg_counter += 1

        logger.info(f"Defined qubit '{q_name}' and classical bit 'c_{q_name}'.")


    def apply_gate(self, gate, q_name, target_q=None):
        if gate in ["h", "x"]:
            if q_name not in self.qubits:
                raise ValueError(f"Qubit '{q_name}' is not defined.")
            if gate == "h":
                self.circuit.h(self.qubits[q_name])
                logger.info(f"Applied Hadamard gate on '{q_name}'.")
            elif gate == "x":
                self.circuit.x(self.qubits[q_name])
                logger.info(f"Applied Pauli-X gate on '{q_name}'.")
        elif gate == "cnot":
            if q_name not in self.qubits:
                raise ValueError(f"Control qubit '{q_name}' is not defined.")
            if target_q not in self.qubits:
                raise ValueError(f"Target qubit '{target_q}' is not defined.")
            self.circuit.cx(self.qubits[q_name], self.qubits[target_q])
            logger.info(f"Applied CNOT gate with control '{q_name}' and target '{target_q}'.")
        else:
            raise ValueError(f"Unknown gate '{gate}'.")

    def alice_send_qubit(self, q_name):
        if q_name not in self.qubits:
            raise ValueError(f"Qubit '{q_name}' is not defined.")

        # Alice randomly selects a bit (0 or 1) and a basis ('+' for rectilinear, 'x' for diagonal)
        bit = random.randint(0, 1)
        basis = random.choice(['+', 'x'])

        self.alice_bits.append(bit)
        self.alice_bases.append(basis)

        # Prepare the qubit based on Alice's bit and basis
        if basis == '+':
            if bit == 1:
                self.circuit.x(self.qubits[q_name])  # Pauli-X (flip) if bit is 1
        elif basis == 'x':
            self.circuit.h(self.qubits[q_name])  # Hadamard for diagonal basis
            if bit == 1:
                self.circuit.x(self.qubits[q_name])

        # Add a barrier to separate operations
        self.circuit.barrier()

        # Log Alice's send and circuit state
        logger.info(f"Alice sent qubit '{q_name}' with bit={bit} and basis='{basis}'.")
        logger.info(f"Current quantum circuit after Alice's send operation:\n{self.circuit}")

    def bob_measure_qubit(self, q_name, basis):
        if q_name not in self.qubits:
            logger.error(f"Error: Qubit '{q_name}' not found in self qubits. Available qubits: {self.qubits.keys()}")
            raise ValueError(f"Qubit '{q_name}' is not defined in self qubits.")

        logger.info(f"Bob is measuring qubit '{q_name}' with basis '{basis}'.")

        # Store Bob's basis
        self.bob_bases.append(basis)

        # Apply the appropriate gate based on Bob's chosen basis
        if basis.upper() == 'H':  # Rectilinear basis
            pass  # No need to apply any gate for rectilinear basis
        elif basis.upper() == 'X':  # Diagonal basis
            self.circuit.h(self.qubits[q_name])  # Apply Hadamard gate for diagonal basis
        else:
            raise ValueError(f"Unknown basis '{basis}' provided for Bob's measurement.")

        # Measure the qubit into the corresponding classical bit
        c_name = f'c_{q_name}'
        if c_name in self.classical_bits:
            try:
                logger.info(f"Measuring qubit '{q_name}' into classical bit '{c_name}'.")
                self.circuit.measure(self.qubits[q_name], self.classical_bits[c_name])
                logger.info(f"Current quantum circuit after Bob's measurement:\n{self.circuit}")
            except Exception as e:
                logger.error(f"Error while measuring qubit '{q_name}': {e}")
                raise
        else:
            logger.error(f"Error: Classical bit for qubit '{q_name}' is not defined.")
            raise ValueError(f"Classical bit for qubit '{q_name}' is not defined.")

  
    def sift_keys(self):
        # Transpile the circuit for the AerSimulator backend
        compiled_circuit = transpile(self.circuit, self.simulator)

        # Execute the transpiled circuit on the AerSimulator
        job = self.simulator.run(compiled_circuit, shots=1)
        result = job.result()
        counts = result.get_counts()
        outcome = list(counts.keys())[0].replace(" ", "")  # Remove any spaces

        logger.info(f"Measurement outcome: {outcome}")

        # Extract Bob's bits based on classical bits
        for q_name in self.qubits:
            c_name = f"c_{q_name}"
            if c_name in self.classical_bits:
                # Qiskit returns bitstrings in little endian; reverse the outcome
                bit_index = list(self.classical_bits.keys()).index(c_name)
                try:
                    bit = int(outcome[::-1][bit_index])
                    self.bob_bits.append(bit)
                except IndexError:
                    logger.error(f"Bit index {bit_index} out of range for outcome '{outcome}'.")
                    return
                except ValueError:
                    logger.error(f"Invalid bit value '{outcome[::-1][bit_index]}' for classical bit '{c_name}'.")
                    return

        # Ensure Alice's and Bob's bases have the same length
        if len(self.alice_bases) != len(self.bob_bases):
            logger.error("Mismatch in the number of Alice's and Bob's bases.")
            return

        # Sift keys where Alice's and Bob's bases match
        self.sifted_alice_bits = []
        self.sifted_bob_bits = []
        for i in range(len(self.alice_bases)):
            alice_basis = self.alice_bases[i]
            bob_basis = self.bob_bases[i]

        # Check if Alice's rectilinear matches Bob's rectilinear, or Alice's diagonal matches Bob's diagonal
        if (alice_basis == '+' and bob_basis == 'H') or (alice_basis == 'x' and bob_basis == 'X'):
            self.shared_key.append(self.alice_bits[i])
            self.sifted_alice_bits.append(self.alice_bits[i])
            self.sifted_bob_bits.append(self.bob_bits[i])
            logger.info(f"Match found! Alice's bit: {self.alice_bits[i]}, Bob's bit: {self.bob_bits[i]}")

        if not self.shared_key:
            logger.warning("No matching bases found. Shared key is empty.")
        else:
            logger.info(f"Sifted key: {self.shared_key}")

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

    def generate_key(self, key_name, num_keys=1, key_length=None):
        """
        Generate one or more shared keys.
    
        :param key_name: Base name for the keys to be generated.
        :param num_keys: Number of keys to generate. Default is 1.
        :param key_length: Desired length of the key(s). If not provided, the full sifted key will be used.
        :raises ValueError: If no shared key is available or if the key length exceeds available bits.
        """

        if not self.shared_key:
            raise ValueError("No shared key available to generate.")
    
        # Determine the maximum key length available from the sifted key
        max_available_length = len(self.shared_key)
    
        if key_length is None:
            key_length = max_available_length
        elif key_length > max_available_length:
            raise ValueError(f"Requested key length {key_length} exceeds available sifted key length {max_available_length}.")
    
        # Generate multiple keys if requested
        keys = []
        for i in range(num_keys):
            # Generate a new key by using `key_length` bits from the shared key
            key = "".join(str(bit) for bit in self.shared_key[:key_length])
        
            # Optionally: Shuffle or rotate the sifted bits for multiple keys
            # (You could rotate or modify the shared key for each subsequent key)
        
            # Add key to the list of generated keys
            keys.append(key)
    
        # Store the generated keys with unique names
        for i, key in enumerate(keys):
            full_key_name = f"{key_name}_{i+1}" if num_keys > 1 else key_name
            setattr(self, full_key_name, key)
            print(f"Generated key '{full_key_name}': {key}")
    
        # Optionally: Return the list of keys for further processing or verification
        return keys

    def print_variable(self, var_name):
        # Schedule the variable for printing after execution
        self.instructions.append(("print", var_name))
        print(f"Scheduled print for variable '{var_name}'.")

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
