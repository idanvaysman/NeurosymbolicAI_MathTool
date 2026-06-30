import ast

class DangerousCodeError(Exception):
    pass

class CodeSanitizer(ast.NodeVisitor):
    DANGEROUS_BUILTINS = {
        'exec', 'eval', 'compile', 'open', 'file', 'input'
    }
    DANGEROUS_MODULES = {
        'os', 'subprocess'
    }

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in self.DANGEROUS_BUILTINS:
            raise DangerousCodeError(f"Dangerous builtin function call: {node.func.id}")
        
        if isinstance(node.func, ast.Attribute):
            module_name = None
            current_node = node.func.value
            while isinstance(current_node, ast.Attribute):
                module_name = f"{current_node.attr}.{module_name}" if module_name else current_node.attr
                current_node = current_node.value
            
            if isinstance(current_node, ast.Name) and current_node.id in self.DANGEROUS_MODULES:
                raise DangerousCodeError(f"Dangerous module call: {current_node.id}.{module_name}")
        
        self.generic_visit(node)

    def sanitize_code(self, code):
        try:
            tree = ast.parse(code)
            self.visit(tree)
            return "Code is safe."
        except DangerousCodeError as e:
            return str(e)

# Example usage
if __name__ == "__main__":
    code_to_check = """
import os
os.system('ls')
"""
    sanitizer = CodeSanitizer()
    result = sanitizer.sanitize_code(code_to_check)
    print(result)
