import os
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx

from legacy_code_assistant.knowledge_base.knowledge_graph.code_graph import CodeUsageGraphBuilder


class RepoCodeGraphGenerator:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.complete_graph = nx.DiGraph()
        self.module_folder_node_count = defaultdict(int)

    def generate_graph(self):
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py') and 'app' in root:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        file_content = f.read()

                    graph_builder = CodeUsageGraphBuilder(file_content, file_path=file_path)
                    graph_builder.analyze_file()
                    self._merge_graph(graph_builder.graph)

                    folder = root.split(os.sep)[-1]
                    self.module_folder_node_count[folder] += len(graph_builder.graph.nodes)

    def _merge_graph(self, partial_graph):
        self.complete_graph = nx.compose(self.complete_graph, partial_graph)

    def get_graph(self):
        return self.complete_graph

    def print_available_modules(self):
        max_value = max(self.module_folder_node_count.values())
        max_modules = [k for k, v in self.module_folder_node_count.items() if v == max_value]
        print(f"Modules/folders with most nodes {max_modules} with {max_value} nodes")

    def print_top_k_modules(self, k):
        sorted_modules = sorted(self.module_folder_node_count.items(), key=lambda x: x[1], reverse=True)
        for i, (module, count) in enumerate(sorted_modules):
            if i == k:
                break
            print(f"{module}: {count}")

    def plot_module_graph(self, module_name):
        graph = self.generate_graph_from_module(module_name)

        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(graph, iterations=15)
        nx.draw(graph, pos, node_size=1000, node_color='red', font_size=12, font_color='blue', with_labels=True)
        plt.show()

    def generate_graph_from_module(self, module_folder):
        module_graph = nx.DiGraph()
        for node, data in self.complete_graph.nodes(data=True):
            if 'file_path' in data and module_folder in data['file_path']:
                module_graph.add_node(node)

        for edge in self.complete_graph.edges():
            if edge[0] in module_graph and edge[1] in module_graph:
                module_graph.add_edge(*edge)

        return module_graph


if __name__ == '__main__':
    repo_path = r'D:\PROJEKTY\LLM-Dec-Hackathon\tests\test_repo'
    generator = RepoCodeGraphGenerator(repo_path)
    generator.generate_graph()
    generator.print_top_k_modules(10)
    generator.plot_module_graph('result')
