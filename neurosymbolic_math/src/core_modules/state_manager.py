import json
import sympy as sp
from typing import List, Dict, Any, Optional

class SymbolicStateManager:
    def __init__(self):
        self.variables = {}
        self.equations = []
        self.constraints = []
        self._backup_state = None  # For transactional state isolation and rollback

    def checkpoint(self):
        """
        Saves a snapshot of the current state to allow rollbacks if 
        downstream agents execute faulty or malicious logic.
        """
        self._backup_state = {
            "variables": {k: v.copy() for k, v in self.variables.items()},
            "equations": list(self.equations),
            "constraints": list(self.constraints)
        }

    def rollback(self) -> bool:
        """
        Restores the state to the last saved checkpoint, isolating state corruption.
        """
        if self._backup_state:
            self.variables = self._backup_state["variables"]
            self.equations = self._backup_state["equations"]
            self.constraints = self._backup_state["constraints"]
            return True
        return False

    def update_variable(self, symbol_name: str, value_expr: str = "", constraints: Optional[List[str]] = None) -> bool:
        """
        Registers or updates a mathematical symbol in the active state.
        Dynamically translates plain language constraints (e.g., 'positive', 'integer')
        into native SymPy keyword assumptions to refine algebraic accuracy.
        """
        try:
            # Map natural language constraint words to SymPy assumptions
            assumptions = {}
            resolved_constraints = constraints or []
            for c in resolved_constraints:
                c_clean = c.lower().strip()
                if "positive" in c_clean:
                    assumptions["positive"] = True
                elif "negative" in c_clean:
                    assumptions["negative"] = True
                
                if "integer" in c_clean:
                    assumptions["integer"] = True
                elif "real" in c_clean:
                    assumptions["real"] = True
                elif "rational" in c_clean:
                    assumptions["rational"] = True

            # Instantiate the SymPy Symbol with bounded assumptions
            symbol_obj = sp.Symbol(symbol_name, **assumptions)
            
            # Parse expression if provided
            parsed_expr = None
            if value_expr:
                # Strip any "SymPy:" prefix if present
                clean_expr = value_expr[6:] if value_expr.startswith("SymPy:") else value_expr
                parsed_expr = sp.sympify(clean_expr)

            self.variables[symbol_name] = {
                "symbol": symbol_obj,
                "expression": parsed_expr,
                "raw_expression": value_expr,
                "constraints": resolved_constraints
            }
            return True
        except Exception:
            return False

    def get_constraints(self, target_symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Queries active boundaries restricting specified symbols.
        """
        if not target_symbols:
            return {"global_constraints": self.constraints}
        return {sym: self.variables.get(sym, {}).get("constraints", []) for sym in target_symbols}

    def register_equation(self, eq_str: str) -> bool:
        """
        Appends a mathematical equation to the stack.
        """
        eq_str = eq_str.strip()
        if eq_str and eq_str not in self.equations:
            self.equations.append(eq_str)
            return True
        return False

    def register_constraint(self, constraint_str: str) -> bool:
        """
        Appends a global algebraic boundary condition to the registry.
        """
        constraint_str = constraint_str.strip()
        if constraint_str and constraint_str not in self.constraints:
            self.constraints.append(constraint_str)
            return True
        return False

    def update_from_json(self, json_str: str) -> bool:
        """
        Parses the verified plan JSON and populates state registries.
        """
        try:
            from core_modules.sanitizer import extract_raw_code
            clean_json = extract_raw_code(json_str)
            data = json.loads(clean_json)
            
            # Save a pre-mutation snapshot to support rollback on parsing errors
            self.checkpoint()

            # Extract variables recursively from AST structure representation
            expr = data.get("mathematical_expression", {})
            if expr:
                def extract_vars(node):
                    vars_found = []
                    if isinstance(node, dict):
                        if node.get("type") == "variable" and "name" in node:
                            vars_found.append(node["name"])
                        for val in node.values():
                            vars_found.extend(extract_vars(val))
                    elif isinstance(node, list):
                        for item in node:
                            vars_found.extend(extract_vars(item))
                    return vars_found
                
                symbols_to_add = list(set(extract_vars(expr)))
                for sym in symbols_to_add:
                    self.update_variable(sym, "")
                    
            # Check for generic calculation string properties
            code = data.get("python_code", "")
            if code:
                if "==" in code:
                    self.register_equation(code)
                else:
                    # Treat it as a variable evaluation path
                    self.register_equation(f"Eq({code}, 0)")
            return True
        except Exception as e:
            print(f"[!] Warning: Failed to parse and update state from JSON plan: {e}")
            self.rollback()  # Safely restore state to uncorrupted status
            return False

    def generate_brief(self) -> Dict[str, Any]:
        """
        Generates a dense, token-efficient mathematical brief.
        """
        return {
            "symbols": list(self.variables.keys()),
            "equations": self.equations,
            "constraints": self.constraints
        }
