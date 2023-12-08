import ast

# from langchain.vectorstores import FaissStore # TODO: we tu wojtek plis zamontuj tego faissa zeby nam dzialalo
from langchain.vectorestores import FAISS
from .embedding_processor import EmbeddingProcessor
from langchain.embeddings import HuggingFaceEmbeddings


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

    def __init__(self, index_name='code-search', model_name='microsoft/codebert-base'):
        """Initialize the Embedding Processor and FaissStore."""
        self.index_name = index_name

        self.model_name = model_name
        self.processor = HuggingFaceEmbeddings(model_name=self.model_name)
        self.vectorstore = None

    def upload_to_faiss(self, data):
        """Encode the data and upload it to Faiss."""

        strings = list(data.values())
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_texts(
                texts=strings, 
                embedding=self.processor,
            )
        else:
            self.vectorstore.add_texts(
                texts=strings, 
                embedding=self.processor,
            )

    def save_index(self):
        """Save the index."""
        self.vectorstore.save(self.index_name)

    def load_index(self):
        """Load the index."""
        self.vectorstore = FAISS.load(self.index_name)



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
