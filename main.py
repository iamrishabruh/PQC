# main.py

import sys
import os
from dsl.interpreter import DSLInterpreter

def main():
    print("Starting DSL Interpreter")

    # Ensure exactly one argument is provided (the script path)
    if len(sys.argv) != 2:
        print("Usage: python main.py <script.dsl>")
        sys.exit(1)
    
    script_path = sys.argv[1]
    print(f"Script path provided: {script_path}")
    
    # Check if the script file exists
    if not os.path.isfile(script_path):
        print(f"Error: Script file '{script_path}' does not exist.")
        sys.exit(1)
    
    # Read the contents of the DSL script
    try:
        with open(script_path, 'r') as file:
            script = file.read()
            print("DSL script successfully read.")
    except Exception as e:
        print(f"Error reading script file: {e}")
        sys.exit(1)
    
    # Initialize the DSLInterpreter with the script content
    interpreter = DSLInterpreter(script)
    print("DSLInterpreter initialized.")
    
    # Execute the interpreter
    interpreter.interpret(script)
    print("DSL Interpreter execution completed.")

if __name__ == "__main__":
    main()
