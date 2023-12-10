import contextlib
import os
import sys

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)

from collections import defaultdict

import networkx as nx
import streamlit as st
from streamlit_agraph import agraph, Config, Edge, Node

from legacy_code_assistant.knowledge_base.knowledge_graph.code_graph import CodeUsageGraphBuilder
from legacy_code_assistant.rag_integration.rag_manager import RagManager


class CodeGraphAnalyzer:
    """
    Analyzes a Python repository to create a graph representing the code usage.
    """
    SMALL, MEDIUM, LARGE = 2, 10, 15
    SIZE_THRESHOLDS = (100, 200)

    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.graph = nx.DiGraph()
        self.module_node_counts = defaultdict(int)

    def analyze_repository(self):
        """Walk through the repository and analyze Python files."""
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py') and 'app' in root:
                    self._analyze_file(os.path.join(root, file))

    def _analyze_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        graph_builder = CodeUsageGraphBuilder(content, file_path=file_path)
        graph_builder.analyze_file()
        self._merge_into_main_graph(graph_builder.graph, self._determine_node_size(len(content)))
        self._update_module_node_count(file_path, len(graph_builder.graph.nodes))

    def _merge_into_main_graph(self, partial_graph, node_size):
        for node in partial_graph.nodes:
            partial_graph.nodes[node]['size'] = node_size
        self.graph = nx.compose(self.graph, partial_graph)

    @staticmethod
    def _determine_node_size(content_length):
        if content_length < CodeGraphAnalyzer.SIZE_THRESHOLDS[0]:
            return CodeGraphAnalyzer.SMALL
        elif content_length < CodeGraphAnalyzer.SIZE_THRESHOLDS[1]:
            return CodeGraphAnalyzer.MEDIUM
        return CodeGraphAnalyzer.LARGE

    def _update_module_node_count(self, file_path, node_count):
        module = os.path.dirname(file_path).split(os.sep)[-1]
        self.module_node_counts[module] += node_count

    def visualize_graph(self, module_name):
        """Visualize the graph for a given module using Streamlit."""
        if module_name:  # Check if module_name is not None
            module_graph = self._generate_module_graph(module_name)
            nodes, edges = self._prepare_nodes_and_edges(module_graph)
            config = Config(width=1200, height=1600, directed=True)
            agraph(nodes=nodes, edges=edges, config=config)
        else:
            st.warning("Please select a module to visualize.")

    def _generate_module_graph(self, module_name):
        module_graph = nx.DiGraph()
        for node, data in self.graph.nodes(data=True):
            if module_name in data.get('file_path', ''):
                module_graph.add_node(node, **data)

        for edge in self.graph.edges(data=True):
            source, target, data = edge
            if source in module_graph and target in module_graph:
                # Add edge with additional data as keyword arguments
                module_graph.add_edge(source, target, **data)
        return module_graph

    @staticmethod
    def _prepare_nodes_and_edges(graph):
        nodes = [Node(id=n, label=n, size=data['size']) for n, data in graph.nodes(data=True)]
        edges = [Edge(source=s, target=t, label=d.get('type', 'N/A')) for s, t, d in graph.edges(data=True)]
        return nodes, edges

    def get_top_modules(self, k):
        """Return top 'k' modules based on the node count."""
        return sorted(self.module_node_counts.items(), key=lambda x: x[1], reverse=True)[:k]

    def get_graph(self, module_name=None):
        if module_name:
            return [(node_id, node_data) for (node_id, node_data) in self.graph.nodes(data=True) if
                    module_name in self.graph.nodes[node_id].get('file_path', '')]
        return self.graph.nodes(data=True)


def get_project_path():
    """Utility function to determine the project path."""
    # return os.path.abspath(osos.path.dirname(__file__))
    return PROJECT_PATH


def main():
    st.set_page_config(page_title="Graph Visualization", layout='wide')
    project_path = get_project_path()
    repo_path = st.sidebar.text_input("Repository Path", os.path.join(project_path, 'tests', 'test_repo'))

    if 'graph_analyzer' not in st.session_state:
        st.session_state['graph_analyzer'] = CodeGraphAnalyzer(repo_path)
        st.session_state['graph_analyzer'].analyze_repository()

    top_modules = st.session_state['graph_analyzer'].get_top_modules(5)
    selected_module = st.sidebar.selectbox("Select Module", [module for module, _ in top_modules])

    prev_module = st.session_state.get('selected_module', None)
    if prev_module is not None and prev_module != selected_module:
        del st.session_state['expanded_classes']
        del st.session_state['expanded_functions']
        del st.session_state['graph']

    st.session_state['selected_module'] = selected_module

    # st.markdown("## Ask LLM")
    # question = st.text_area("", key='general_ask_llm')
    # if question:
    #     process_prompt('Analyze', question, None)
        
    col1, col2 = st.columns([2, 1])
    generate_graph_button = st.sidebar.button('Generate Graph')

    with col1:
        if generate_graph_button or 'graph' not in st.session_state:
            st.session_state['graph_analyzer'].analyze_repository()
            st.markdown("## Code Usage Graph")
            st.session_state['graph_analyzer'].visualize_graph(selected_module)
            st.session_state['graph'] = st.session_state['graph_analyzer'].get_graph()

    with col2:
        if 'graph' in st.session_state:
            st.markdown("## Module Details")
            display_node_details(st.session_state['graph_analyzer'], selected_module)


def display_node_details(graph_analyzer, module_name, top_k=10):
    module_graph = graph_analyzer.get_graph(module_name)

    node_counter = 0
    for node_id, node_data in module_graph:
        if node_counter >= top_k:
            break
        node_counter += 1

        with contextlib.suppress(IOError):
            with open(node_data.get('file_path', ''), 'r') as file:
                file_content = file.read()

            if file_content.strip():
                graph_builder = CodeUsageGraphBuilder(file_content, file_path=node_data['file_path'])
                graph_builder.analyze_file()
                display_class_function_details(graph_builder, node_id)
                st.markdown(f"**File Path**: [`{node_data.get('file_path', '')}`]({node_data.get('file_path', '')})")
                st.markdown("---")  # Separator for each node


def display_class_function_details(graph_builder, node_id):
    """Display details of classes and functions in the node with an 'Ask LLM' button."""

    if 'expanded_classes' not in st.session_state:
        st.session_state['expanded_classes'] = {class_name + str(node_id): False for class_name in graph_builder.code_extractor.classes.keys()}
    else:
        for class_name in graph_builder.code_extractor.classes.keys():
            elem_id = class_name + str(node_id) 
            if elem_id not in st.session_state['expanded_classes']:
                st.session_state['expanded_classes'][elem_id] = False

    if 'expanded_functions' not in st.session_state:
        st.session_state['expanded_functions'] = {func_name + str(node_id): False for func_name in graph_builder.code_extractor.functions.keys()}
    else:
        for func_name in graph_builder.code_extractor.functions.keys():
            elem_id = func_name + str(node_id)
            if elem_id not in st.session_state['expanded_functions']:
                st.session_state['expanded_functions'][elem_id] = False


    for class_name, class_info in graph_builder.code_extractor.classes.items(): 

        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"#### Class: {class_name}")
        with col1:
            expanded = st.session_state['expanded_classes'][class_name + str(node_id)]
            expand_button = st.button('🚀 Ask LLM', key=f'ask_llm_class_{node_id}_{class_name}')

            if expand_button or expanded:
                # with st.expander("LLM Prompts", expanded=expanded):
                st.session_state['expanded_classes'][class_name + str(node_id)] = True

                st.markdown(f"#### LLM Prompts")
                selected_prompt = st.selectbox("Select a prompt template:",
                                                ["Modify", "Write Tests", "Search for Vulnerabilities",
                                                 'Explain', 'Refactor'],
                                                key=f'prompt_select_{node_id}')
                additional_info = st.text_area("Additional information:", key=f'additional_info_{node_id}')

                if st.button("Submit to LLM", key=f'submit_llm_{node_id}'):
                    process_prompt(selected_prompt, additional_info, node_id, class_info.source_code)
        st.text(f"Docstring: {class_info.docstring}")
        st.markdown("```python\n" + class_info.source_code + "\n```")

    for func_name, func_info in graph_builder.code_extractor.functions.items():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"#### Function: {func_name}")
        with col1:
            expanded = st.session_state['expanded_functions'][func_name + str(node_id)]
            expand_button = st.button('🚀 Ask LLM', key=f'ask_llm_func_{node_id}_{func_name}')

            if expand_button or expanded:
                # with st.expander("LLM Prompts", expanded=st.session_state['expanded_functions'][func_name]):
                st.session_state['expanded_functions'][func_name + str(node_id)] = True

                st.markdown(f"#### LLM Prompts")
                selected_prompt = st.selectbox("Select a prompt template:",
                                                ["Modify", "Write Tests", "Search for Vulnerabilities",
                                                 'Explain', 'Refactor'],
                                                key=f'prompt_select_{node_id}')
                additional_info = st.text_area("Additional information:", key=f'additional_info_{node_id}')

                if st.button("Submit to LLM", key=f'submit_llm_{node_id}'):
                    process_prompt(selected_prompt, additional_info, node_id, class_info.source_code)
        st.text(f"Docstring: {func_info.docstring}")
        st.markdown("```python\n" + func_info.source_code + "\n```")


def process_prompt(prompt_template, additional_info, node_id, source_code=None):
    # Placeholder function to process the prompt
    # TODO: RAG model processing logic here - bois please do this jesli możecie
    
    st.write(
        f"Processing {prompt_template} with {additional_info} for node {node_id}")  # Here you would integrate your RAG model processing logic

    manager = RagManager('credentials.yaml', 'docstring_based_index', 'credentials.yaml')
    if prompt_template == 'Modify': # modifyPrompt - context provided
        print(additional_info)
        print('-'*50)
        print(source_code)
        
        result = manager.modify_code(additional_info, context=source_code)
    elif prompt_template == 'Analyze': # analyzePrompt - retrieve context
        result = manager.analyze_code(additional_info)
    elif prompt_template == 'Add Code': # addPrompt - retrieve context
        result = manager.add_code(additional_info)
    elif prompt_template == 'Write Tests': # testPrompt - context provided
        result = manager.write_tests(additional_info, context=source_code)
    elif prompt_template == 'Search for Vulnerabilities': # vulnerabilityPrompt - context provided
        result = manager.search_for_vulnerabilities(additional_info, context=source_code)
    elif prompt_template == 'Ask Question': 
        raise NotImplementedError
    elif prompt_template == 'Refactor':
        raise NotImplementedError
    else:
        raise ValueError(f"Invalid prompt template: {prompt_template}")

    st.markdown(result)

if __name__ == '__main__':
    main()
