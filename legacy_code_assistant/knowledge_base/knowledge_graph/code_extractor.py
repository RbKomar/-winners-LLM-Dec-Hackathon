import ast
import astor


class ClassItem:
    def __init__(self, name, docstring, code, bases=None):
        if bases is None:
            bases = []
        self.name = name
        self.docstring = docstring
        self.code = code
        self.bases = bases
        self.functions = {}
        self.usage = {}

    def add_usage(self, callee):
        self.usage[callee] = self.usage.get(callee, 0) + 1
        print(f"Adding class usage: {self.name} -> {callee}")


class FunctionItem:
    def __init__(self, name, docstring, code):
        self.name = name
        self.docstring = docstring
        self.code = code
        self.usage = {}
        self.path = None

    def add_usage(self, callee):
        self.usage[callee] = self.usage.get(callee, 0) + 1
        print(f"Adding function usage: {self.name} -> {callee}")


class CodeExtractor(ast.NodeVisitor):
    def __init__(self, file_content):
        self.file_content = file_content.splitlines()
        self.classes = {}
        self.functions = {}
        self.current_class = None
        self.current_function = None

    def visit_ClassDef(self, node):
        base_names = [base.id for base in node.bases if isinstance(base, ast.Name)]
        self.current_class = self.classes[node.name] = ClassItem(
            node.name, ast.get_docstring(node), astor.to_source(node), base_names)
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        function_item = FunctionItem(node.name, ast.get_docstring(node), astor.to_source(node))
        if self.current_class:
            self.current_function = self.current_class.functions[node.name] = function_item
        else:
            self.current_function = self.functions[node.name] = function_item
        self.generic_visit(node)
        self.current_function = None

    def visit_Call(self, node):
        callee = self._get_callee(node)
        if callee and self.current_function:
            callee = self._check_class_method(callee)
            self.current_function.add_usage(callee)

    def _get_callee(self, node):
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            instance_name = node.func.value.id
            method_name = node.func.attr
            return f"{instance_name}.{method_name}" if instance_name in self.classes else method_name

        elif isinstance(node.func, ast.Name):
            callee = node.func.id
            return f"{callee}.__init__" if callee in self.classes else callee
        return None

    def _check_class_method(self, callee):
        if '.' not in callee:
            for class_item in self.classes.values():
                if callee in class_item.functions:
                    return f"{class_item.name}.{callee}"
        return callee


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
