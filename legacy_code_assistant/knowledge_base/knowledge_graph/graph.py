import contextlib
import pathlib
from collections import defaultdict

import git
import networkx as nx

from knowledge_base.knowledge_graph.code_extractor import extract_classes_methods

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


def main():
    repo_path = r'C:\Users\ml\PycharmProjects\LLM-Dec-Hackathon\tests\test_repo'
    analyzer = RepoAnalyzer(repo_path)
    commits_data = analyzer.get_repo_commits()
    files_metadata = analyzer.get_repo_files_metadata()
    graph, _ = analyzer.build_commit_dependency_graph(commits_data, files_metadata)

    print("Sample Nodes:", list(graph.nodes(data=True))[:10])
    print("Sample Edges:", list(graph.edges(data=True))[:10])

    # In the main function
    commit_id_to_analyze = 'fabbfe76f07f668ea8b4502522dc2f401d4f19bd'
    affected_nodes = analyzer.query_commit_dependency_graph(graph, commit_id_to_analyze)
    print(f"Nodes affected by commit {commit_id_to_analyze}:", affected_nodes)

    # After building the graph
    hotspots = {node: data for node, data in graph.nodes(data=True) if
                data['type'] in [NODE_TYPE_CLASS, NODE_TYPE_METHOD] and data.get('modification_count', 0) > 2}
    print("Potential Refactoring Hotspots:", hotspots)

    # Utilizing the extracted classes and methods
    for cls, cls_data in files_metadata['classes'].items():
        print(f"Class: {cls}\nDocumentation: {cls_data['docstring']}\nCode:\n{cls_data['code']}\n")

    for method, method_data in files_metadata['methods'].items():
        print(f"Method: {method}\nDocumentation: {method_data['docstring']}\nCode:\n{method_data['code']}\n")

    # Analyzing commit authors
    author_to_code_segments = defaultdict(set)
    for commit in commits_data:
        for file in commit['files']:
            author_to_code_segments[commit['author']].add(file)

    for author, files in author_to_code_segments.items():
        print(f"Author: {author}\nFiles Worked On: {files}\n")


if __name__ == "__main__":
    main()
