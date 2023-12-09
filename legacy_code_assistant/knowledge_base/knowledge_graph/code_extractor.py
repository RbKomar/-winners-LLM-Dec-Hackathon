import ast


class CodeExtractor(ast.NodeVisitor):
    def __init__(self, file_content):
        self.file_content = file_content.splitlines()
        self.classes = {}
        self.functions = {}
        self.current_class = None

    def get_source_segment(self, node):
        start_line = node.lineno - 1
        end_line = node.end_lineno  # inclusive
        return '\n'.join(self.file_content[start_line:end_line])

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
def foo():
    '''This is a docstring for foo.'''
    pass

class Bar:
    '''This is a docstring for Bar class.'''
    def baz(self):
        '''This is a docstring for baz.'''
        pass
    """

    metadata = extract_classes_methods(file_content)
    print(metadata)
