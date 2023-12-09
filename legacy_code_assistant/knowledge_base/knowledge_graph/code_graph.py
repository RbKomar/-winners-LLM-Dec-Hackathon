import ast

import matplotlib.pyplot as plt
import networkx as nx

from legacy_code_assistant.knowledge_base.knowledge_graph.code_extractor import CodeExtractor


class CodeUsageGraphBuilder:
    def __init__(self, file_content, repo_path=None, file_path=None):
        self.file_content = file_content
        self.repo_path = repo_path
        self.graph = nx.DiGraph()
        self.code_extractor = CodeExtractor(self.file_content, file_path)

    def analyze_file(self):
        tree = ast.parse(self.file_content)
        self.code_extractor.visit(tree)

        self._add_class_nodes_and_edges()
        self._add_function_nodes_and_edges()
        self._add_inheritance_edges()

    def _add_class_nodes_and_edges(self):
        for class_name, class_info in self.code_extractor.classes.items():
            self.graph.add_node(class_name, item=class_info, type='class', file_path=class_info.file_path)
            for method_name, method_info in class_info.functions.items():
                method_full_name = f'{class_name}.{method_name}'
                self.graph.add_node(method_full_name, type='method', file_path=method_info.file_path)
                self.graph.add_edge(class_name, method_full_name, type='consist')

                for callee, count in method_info.usage.items():
                    self.graph.add_edge(method_full_name, callee, type='calls', weight=count)

    def _add_function_nodes_and_edges(self):
        for func_name, func_info in self.code_extractor.functions.items():
            self.graph.add_node(func_name, item=func_info, type='function', file_path=func_info.file_path)
            for callee, count in func_info.usage.items():
                self.graph.add_edge(func_name, callee, type='calls', weight=count)

    def _add_inheritance_edges(self):
        for class_name, class_info in self.code_extractor.classes.items():
            for base_class in class_info.bases:
                self.graph.add_edge(class_name, base_class, type='inherit')

    def print_graph(self):
        print("Edge List: ")
        print(self.graph.edges(data=True))
        print("Node List: ")

    def visualize_graph(self):
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue', edge_color='gray')
        plt.show()


if __name__ == '__main__':
    example_code = """
class BaseClass:
    pass

class MyClass(BaseClass):
    def method1(self):
        pass

    def method2(self):
        self.method1()

def function1():
    mc = MyClass()
    mc.method1()

function1()
    """

    graph_builder = CodeUsageGraphBuilder(example_code)
    graph_builder.analyze_file()
    graph_builder.print_graph()
    graph_builder.visualize_graph()
