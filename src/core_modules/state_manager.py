import sympy as sp

class SymbolicStateManager:
    def __init__(self):
        self.symbols = {}
        self.equation_stack = []
        self.constraint_vector = []

    def register_symbol(self, symbol_name, value):
        if isinstance(value, str) and value.startswith('SymPy:'):
            # Assuming the value is a SymPy expression in string format
            value = sp.sympify(value[6:])
        self.symbols[symbol_name] = value

    def get_symbol_value(self, symbol_name):
        return self.symbols.get(symbol_name)

    def update_variable(self, variable_name, new_value):
        if variable_name in self.symbols:
            self.symbols[variable_name] = new_value
        else:
            raise KeyError(f"Variable {variable_name} not found.")

    def get_constraints(self):
        return self.constraint_vector

    def generate_brief(self):
        brief = {
            "symbols": self.symbols,
            "equations": [str(eq) for eq in self.equation_stack],
            "constraints": [str(constraint) for constraint in self.constraint_vector]
        }
        return brief
