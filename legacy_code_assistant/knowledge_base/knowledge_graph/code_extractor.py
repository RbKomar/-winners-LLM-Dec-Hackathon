import ast
import astor

class CodeExtractor(ast.NodeVisitor):
    def __init__(self, file_content):
        self.file_content = file_content.splitlines()
        self.classes = {}
        self.functions = {}
        self.current_class = None

    def visit_ClassDef(self, node):
        class_docstring = ast.get_docstring(node)
        class_code = astor.to_source(node)
        self.current_class = node.name
        self.classes[node.name] = {
            'docstring': class_docstring, 'code': class_code,
            'code_start_line': node.lineno, 'code_end_line': node.end_lineno
            }
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        func_docstring = ast.get_docstring(node)
        func_code = astor.to_source(node)
        func_key = (self.current_class, node.name) if self.current_class else node.name
        self.functions[func_key] = {
            'docstring': func_docstring, 'code': func_code,
            'code_start_line': getattr(node, 'lineno', None), 'code_end_line': getattr(node, 'end_lineno', None)
            }
        

def extract_classes_methods(file_content):
    tree = ast.parse(file_content)
    extractor = CodeExtractor(file_content)
    extractor.visit(tree)
    return extractor.classes, extractor.functions


def extract_all(file_content):
    tree = ast.parse(file_content)
    extractor = CodeExtractor(file_content)
    extractor.visit(tree)

    # Extract the module code
    module_code = astor.to_source(tree)
    module = {
        'docstring': ast.get_docstring(tree), 'code': module_code,
        'code_start_line': 0, 'code_end_line': None
    }
    
    return extractor.classes, extractor.functions, module


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
