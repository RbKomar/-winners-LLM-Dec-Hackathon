import ast

from langchain.vectorstores import FaissStore # TODO: we tu wojtek plis zamontuj tego faissa zeby nam dzialalo
from .embedding_processor import EmbeddingProcessor

# TODO: i tu tez zamontuj tego faissa
class KnowledgeBaseBuilder:
    """
    A class used to represent a Knowledge Base Builder.

    Attributes
    ----------
    processor : EmbeddingProcessor
        an instance of the EmbeddingProcessor class
    index_name : str
        the name of the index used in Faiss
    index : FaissStore
        the FaissStore instance
    """

    def __init__(self, index_name='code-search'):
        """Initialize the Embedding Processor and FaissStore."""
        self.processor = EmbeddingProcessor()
        self.index_name = index_name
        self.index = FaissStore(index_name)

    def upload_to_faiss(self, data):
        """Encode the data and upload it to Faiss."""
        vectors = [(key, self.processor.encode(value)) for key, value in data.items()]
        for vector in vectors:
            vector_id, encoded_vector = vector
            self.index.insert(vector_id, encoded_vector)


class CodeAnalyzer:
    """
    A class used to analyze code files.

    Attributes
    ----------
    code_files : list
        a list of code files to analyze
    """

    def __init__(self, code_files):
        self.code_files = code_files

    @property
    def analyzed(self):
        """Return a list of analyzed functions."""
        return [self.extract_function_info(item) for file in self.code_files for item in
                ast.walk(ast.parse(open(file, 'r').read())) if isinstance(item, ast.FunctionDef)]

    @staticmethod
    def extract_function_info(function_node):
        """
        Extract function information.

        Returns
        -------
        dict
            a dictionary containing function name and function docstring.
        """
        return {'name': function_node.name, 'docstring': ast.get_docstring(function_node)}
