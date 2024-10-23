# dsl/interpreter.py

from .parser import parse
from .commands import Commands

class DSLInterpreter:
    def __init__(self, data):
        print("Initializing DSLInterpreter...")
        self.parser = parse(data)
        self.commands = Commands()
        print("DSLInterpreter initialized successfully.")

    def interpret(self, script):
        print("Starting interpretation of the script...")
        try:
            # Parse the script
            parsed_commands = self.parser(script)
            print(f"Parsed commands: {parsed_commands}")
        except SyntaxError as e:
            print(f"Parsing Error: {e}")
            return
        except Exception as e:
            print(f"Unexpected Parsing Error: {e}")
            return

        if not parsed_commands:
            print("No commands to execute.")
            return

        # Execute each command in the parsed script
        for idx, cmd in enumerate(parsed_commands, start=1):
            print(f"Executing command {idx}: {cmd}")
            action = cmd[0]
            try:
                if action == 'qubit':
                    self.commands.define_qubit(cmd[1])
                elif action in ['h', 'x']:
                    self.commands.apply_gate(action, cmd[1])
                elif action == 'cnot':
                    self.commands.apply_gate(action, cmd[1], cmd[2])
                elif action == 'measure':
                    self.commands.measure_qubit(cmd[1], cmd[2])
                elif action == 'print':
                    self.commands.print_variable(cmd[1])
                elif action == 'alice_send':
                    self.commands.alice_send_qubit(cmd[1])
                elif action == 'bob_measure':
                    self.commands.bob_measure_qubit(cmd[1], cmd[2])
                elif action == 'sift_keys':
                    self.commands.sift_keys()
                elif action == 'check_eavesdropping':
                    self.commands.check_eavesdropping()
                elif action == 'generate_key':
                    self.commands.generate_key(cmd[1])
                elif action == 'eavesdrop':
                    self.commands.execute_eavesdropping()
                else:
                    print(f"Unknown action '{action}' encountered.")
            except ValueError as ve:
                print(f"Execution Error: {ve}")
                return
            except Exception as ex:
                print(f"Unexpected Error: {ex}")
                return

        # After executing all commands, handle print instructions
        self.execute_prints()
        print("Interpretation of the script completed.")

    def execute_prints(self):
        print("Executing print instructions...")
        for instr in self.commands.instructions:
            if instr[0] == 'print':
                var_name = instr[1]
                print(f"Handling print for variable: {var_name}")
                # Check if it's a classical bit
                if var_name.startswith('c'):
                    if var_name in self.commands.classical_bits:
                        bit = self.retrieve_bit_value(var_name)
                        print(f"{var_name} = {bit}")
                    else:
                        print(f"Print Error: Classical bit '{var_name}' is not defined.")
                elif var_name.startswith('k'):
                    # It's a secret key
                    if hasattr(self.commands, var_name):
                        key = getattr(self.commands, var_name)
                        print(f"{var_name} = {key}")
                    else:
                        print(f"Print Error: Key '{var_name}' is not defined.")
                else:
                    print(f"Print Error: Unknown variable '{var_name}'.")

    def retrieve_bit_value(self, c_name):
        # Retrieve the measurement outcome from the shared key if possible
        # Since the actual measurement is done in 'sift_keys', and the sifted key is stored
        # Here, we should map classical bits to their measured values
        # However, in the current 'Commands' class, individual classical bit values are not stored
        # To implement this, we need to store measurement results in the 'Commands' class
        # For simplicity, we'll simulate the retrieval by accessing 'bob_bits'

        # Extract the index based on classical bit name
        try:
            index = list(self.commands.classical_bits.keys()).index(c_name)
            if index < len(self.commands.bob_bits):
                bit = self.commands.bob_bits[index]
                print(f"Retrieved bit value for {c_name}: {bit}")
                return bit
            else:
                print(f"Bit index for {c_name} is out of range.")
                return "Undefined"
        except ValueError:
            print(f"Classical bit '{c_name}' not found.")
            return "Undefined"
