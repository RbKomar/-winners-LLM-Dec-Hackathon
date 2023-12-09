import ast

class CodeExtractor(ast.NodeVisitor):
    def __init__(self, file_content):
        self.file_content = file_content.splitlines()
        self.classes = {}
        self.functions = {}
        self.current_class = None

    def get_source_segment(self, node):
        start_line = node.lineno
        end_line = node.end_lineno  # Inclusive

        # Handling multiline docstrings
        if hasattr(node, 'body') and node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            docstring_node = node.body[0]
            if hasattr(docstring_node, 'end_lineno'):
                start_line = docstring_node.end_lineno + 1
            else:
                # Fallback for single-line docstrings or Python versions without end_lineno
                start_line += len(ast.get_docstring(node).splitlines())

        return '\n'.join(self.file_content[start_line - 1:end_line]).strip()

    def visit_ClassDef(self, node):
        class_docstring = ast.get_docstring(node)
        class_code = self.get_source_segment(node)
        self.current_class = node.name
        self.classes[node.name] = {'docstring': class_docstring, 'code': class_code}
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        func_docstring = ast.get_docstring(node)
        func_code = self.get_source_segment(node)
        func_key = (self.current_class, node.name) if self.current_class else node.name
        self.functions[func_key] = {'docstring': func_docstring, 'code': func_code}

def extract_classes_methods(file_content):
    tree = ast.parse(file_content)
    extractor = CodeExtractor(file_content)
    extractor.visit(tree)
    return extractor.classes, extractor.functions


if __name__ == '__main__':
    file_content = """
# This is a module-level comment
def global_function():
    '''This is a docstring for global_function.'''
    pass

class ComplexClass:
    '''This is a docstring for ComplexClass.'''
    
    class_nested = "This is a nested class variable."
    
    def __init__(self):
        '''This is a docstring for the constructor of ComplexClass.'''
        self.instance_variable = 42

    def instance_method(self):
        '''This is a docstring for instance_method.'''
        return self.instance_variable

    @staticmethod
    def static_method():
        '''This is a docstring for static_method.'''
        return "This is a static method."

    @classmethod
    def class_method(cls):
        '''This is a docstring for class_method.'''
        return "This is a class method."

def another_global_function():
    '''This is another global function.'''
    pass
    """
    metadata = extract_classes_methods(file_content)
    print(metadata)
