import difflib
import sys

sys.path.append('D:\\PROJEKTY\\LLM-Dec-Hackathon')

import contextlib
import pathlib
from collections import defaultdict

import git
import networkx as nx
import streamlit as st

from legacy_code_assistant.knowledge_base.knowledge_graph.code_extractor import extract_classes_methods

# Constants
NODE_TYPE_COMMIT = "commit"
NODE_TYPE_FILE = "file"
NODE_TYPE_CLASS = "class"
NODE_TYPE_METHOD = "method"
EDGE_TYPE_MODIFIED = "modifies"
EDGE_TYPE_CONTAINS = "contains"


class RepoAnalyzer:
    def __init__(self, repo_path):
        self.repo = git.Repo(repo_path)
        self.graph = nx.DiGraph()

    def get_repo_commits(self):
        return [
            {'commit_id': commit.hexsha, 'author': commit.author.name, 'date': commit.committed_datetime.isoformat(),
             'message': commit.message.strip(), 'files': list(commit.stats.files.keys()), } for commit in
            self.repo.iter_commits()]

    def get_repo_files_metadata(self):
        files_metadata = defaultdict(dict)
        for file in self.repo.tree().traverse():
            if file.type == 'blob':
                with contextlib.suppress(Exception):
                    content = pathlib.Path(file.abspath).read_text()
                    classes, methods = extract_classes_methods(content)
                    files_metadata[file.path]['classes'] = list(classes.keys())
                    files_metadata[file.path]['methods'] = [m[1] if isinstance(m, tuple) else m for m in methods.keys()]
        return files_metadata

    def build_commit_dependency_graph(self, commits_data, files_metadata):
        class_modification_counts = defaultdict(int)
        for commit in commits_data:
            commit_node = commit['commit_id']
            self.graph.add_node(commit_node, type=NODE_TYPE_COMMIT, author=commit['author'], date=commit['date'],
                                message=commit['message'])
            for file in commit['files']:
                file_node = f"file_{file}"
                self.graph.add_node(file_node, type=NODE_TYPE_FILE)
                self.graph.add_edge(commit_node, file_node, type=EDGE_TYPE_MODIFIED)
                for cls in files_metadata.get(file, {}).get('classes', []):
                    class_node = f"class_{file}_{cls}"
                    self.graph.add_node(class_node, type=NODE_TYPE_CLASS, belongs_to_file=file,
                                        modification_count=class_modification_counts[class_node] + 1)
                    self.graph.add_edge(file_node, class_node, type=EDGE_TYPE_CONTAINS)
                    class_modification_counts[class_node] += 1
                for method in files_metadata.get(file, {}).get('methods', []):
                    method_node = f"method_{file}_{method}"
                    self.graph.add_node(method_node, type=NODE_TYPE_METHOD, belongs_to_file=file)
                    if 'class_node' in locals():
                        self.graph.add_edge(class_node, method_node, type=EDGE_TYPE_CONTAINS)
        return self.graph, class_modification_counts

    @staticmethod
    def query_commit_dependency_graph(graph, commit_id):
        return list(nx.descendants(graph, commit_id))

    def get_function_modifications(self, EMPTY_TREE_SHA=None):
        function_modifications = defaultdict(list)
        for commit in self.repo.iter_commits():
            # Using the diff to find changes in the commit
            parent = commit.parents[0] if commit.parents else EMPTY_TREE_SHA
            diffs = {
                diff.a_path: diff for diff in commit.diff(parent)
            }

            for diff in diffs.values():
                if diff.change_type in ['A', 'M']:  # Added or modified files
                    # Extracting methods and their changes
                    methods = self.extract_methods_from_diff(diff)
                    for method, changes in methods.items():
                        function_modifications[method].append({
                            'commit_id': commit.hexsha,
                            'date': commit.committed_datetime.isoformat(),
                            'changes': changes
                        })
        return function_modifications

    def extract_methods_from_diff(self, diff):
        method_changes = defaultdict(str)
        # Assuming we are working with Python files for simplicity
        if diff.a_path.endswith(".py"):
            a_blob = diff.a_blob.data_stream.read().decode('utf-8') if diff.a_blob else ''
            b_blob = diff.b_blob.data_stream.read().decode('utf-8') if diff.b_blob else ''

            # Getting the diff lines
            diff_lines = list(difflib.unified_diff(a_blob.splitlines(), b_blob.splitlines()))

            current_method = None
            for line in diff_lines:
                if line.startswith('@@'):
                    current_method = None
                elif line.startswith('+') or line.startswith('-'):
                    if 'def ' in line:
                        current_method = line.split('def ')[1].split('(')[0].strip()
                    if current_method:
                        method_changes[current_method] += line + '\n'
        return method_changes


def visualize_function_evolution(function_modifications):
    st.title("Function Evolution Over Time")
    sorted_functions = sorted(function_modifications.items(), key=lambda x: len(x[1]), reverse=True)

    # Ensure a function is selected by default
    selected_function_name, modifications = st.selectbox("Select a function:", sorted_functions,
                                                         format_func=lambda x: f"{x[0]} ({len(x[1])} modifications)",
                                                         index=0)
    if selected_function_name:
        visualize_modifications(modifications)
    else:
        st.text("No modifications found for the selected function.")


def visualize_modifications(modifications):
    function_change_dates = [mod['date'] for mod in modifications]
    # Reverse the order of dates
    function_change_dates.reverse()
    modifications.reverse()

    # Using the index of the modification as the slider value
    time_index = st.select_slider("Select a point in time", options=range(len(function_change_dates)),
                                  format_func=lambda x: function_change_dates[x], key="time_slider")

    selected_modification = modifications[time_index]
    st.code(selected_modification['changes'], language='python')


def main():
    repo_path = r'D:\\PROJEKTY\\LLM-Dec-Hackathon\\tests\\test_repo'
    analyzer = RepoAnalyzer(repo_path)
    commits = analyzer.get_repo_commits()
    files_metadata = analyzer.get_repo_files_metadata()
    _, _ = analyzer.build_commit_dependency_graph(commits, files_metadata)

    function_modifications = analyzer.get_function_modifications()
    visualize_function_evolution(function_modifications)


def past_examp(files_metadata, graph, analyzer, commits_data):
    print("Sample Nodes:", list(graph.nodes(data=True))[:10])
    print("Sample Edges:", list(graph.edges(data=True))[:10])

    commit_id_to_analyze = 'fabbfe76f07f668ea8b4502522dc2f401d4f19bd'
    affected_nodes = analyzer.query_commit_dependency_graph(graph, commit_id_to_analyze)
    print(f"Nodes affected by commit {commit_id_to_analyze}:", affected_nodes)
    hotspots = {node: data for node, data in graph.nodes(data=True) if
                data['type'] in [NODE_TYPE_CLASS, NODE_TYPE_METHOD] and data.get('modification_count', 0) > 2}

    for cls, cls_data in files_metadata['classes'].items():
        print(f"Class: {cls}\nDocumentation: {cls_data['docstring']}\nCode:\n{cls_data['code']}\n")

    for method, method_data in files_metadata['methods'].items():
        print(f"Method: {method}\nDocumentation: {method_data['docstring']}\nCode:\n{method_data['code']}\n")

    author_to_code_segments = defaultdict(set)
    for commit in commits_data:
        for file in commit['files']:
            author_to_code_segments[commit['author']].add(file)

    for author, files in author_to_code_segments.items():
        print(f"Author: {author}\nFiles Worked On: {files}\n")


if __name__ == "__main__":
    main()
