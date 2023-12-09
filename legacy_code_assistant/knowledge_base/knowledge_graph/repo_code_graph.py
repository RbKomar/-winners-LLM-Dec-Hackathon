import os
import sys
from collections import defaultdict

import networkx as nx
import streamlit as st
from streamlit_agraph import agraph, Config, Edge, Node

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_path)

from legacy_code_assistant.knowledge_base.knowledge_graph.code_graph import CodeUsageGraphBuilder


class RepoCodeGraphGenerator:
    def __init__(self, repo_path):
        """Initialize the RepoCodeGraphGenerator with a repository path."""
        self.repo_path = repo_path
        self.complete_graph = nx.DiGraph()
        self.module_folder_node_count = defaultdict(int)

    def analyze_repo(self):
        """
        Analyze the repo, generate a graph of code usage and count nodes per module folder.
        """
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py') and 'app' in root:
                    self.analyze_file(os.path.join(root, file))

    def analyze_file(self, file_path):
        """Analyze a python file in the provided path."""
        with open(file_path, 'r') as f:
            file_content = f.read()

        size = self._get_binned_size(len(file_content))
        graph_builder = CodeUsageGraphBuilder(file_content, file_path=file_path)
        graph_builder.analyze_file()
        self._merge_graph(graph_builder.graph, size)

        folder = os.path.dirname(file_path).split(os.sep)[-1]
        self.module_folder_node_count[folder] += len(graph_builder.graph.nodes)

    def _add_node_edges(self, graph):
        """Add nodes and its edges to the graph provided."""
        nodes = [Node(id=n, label=n, size=data['size'], metadata={key: data[key] for key in data}) for n, data in
                 graph.nodes(data=True)]
        edges = [Edge(source=source, target=target, label=data.get('type', 'N/A')) for source, target, data in
                 graph.edges(data=True)]
        return nodes, edges

    def _merge_graph(self, partial_graph, size):
        for node in list(partial_graph.nodes):
            partial_graph.nodes[node]['size'] = size
        self.complete_graph = nx.compose(self.complete_graph, partial_graph)

    @staticmethod
    def _get_binned_size(length):
        if length < 100:
            return 5
        elif length < 200:
            return 10
        else:
            return 15

    def get_graph(self):
        return self.complete_graph

    def print_available_modules(self):
        max_value = max(self.module_folder_node_count.values())
        max_modules = [k for k, v in self.module_folder_node_count.items() if v == max_value]
        print(f"Modules/folders with most nodes {max_modules} with {max_value} nodes")

    def get_top_k_modules(self, k):
        sorted_modules = sorted(self.module_folder_node_count.items(), key=lambda x: x[1], reverse=True)
        return [module for module, count in sorted_modules[:k]]

    def generate_graph_from_module(self, module_folder):
        module_graph = nx.DiGraph()
        for node, data in self.complete_graph.nodes(data=True):
            if 'file_path' in data and 'size' in data and module_folder in data['file_path']:
                module_graph.add_node(node, size=data['size'])

        for edge in self.complete_graph.edges(data=True):
            if edge[0] in module_graph.nodes() and edge[1] in module_graph.nodes() and 'type' in edge[2]:
                module_graph.add_edge(edge[0], edge[1], **edge[2])

        return module_graph

    def plot_module_graph(self, module_name):
        """Plot graph of a provided module name."""
        graph = self.generate_graph_from_module(module_name)
        nodes, edges = self._add_node_edges(graph)
        # Capture the event data
        config = Config(width=1200, height=600, directed=True)
        agraph(nodes=nodes, edges=edges, config=config)
        return graph

    @staticmethod
    def show_node_details(graph):
        """Add a Tab with details of each node in the graph."""
        nodes = list(graph.nodes(data=True))
        if st.sidebar.button("Show Node Details"):
            st.sidebar.markdown("## Node Details")
            node_id = st.sidebar.selectbox("Select a node", options=[node[0] for node in nodes], index=0)
            if selected_node := next((node for node in nodes if node[0] == node_id), None):
                st.sidebar.json(selected_node[1])


if __name__ == '__main__':
    st.set_page_config(page_title="Graph Visualization", page_icon=":bar_chart:", layout='wide',
                       initial_sidebar_state='expanded')
    project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    repo_path = st.sidebar.text_input("Repository Path", project_path + '\\tests\\test_repo')
    generator = RepoCodeGraphGenerator(repo_path)
    generator.analyze_repo()
    top_k_modules = generator.get_top_k_modules(5)
    module_name = st.sidebar.selectbox("Module Name", top_k_modules)
    if st.sidebar.button('Generate Graph'):
        graph = generator.plot_module_graph(module_name)
        generator.show_node_details(graph)
