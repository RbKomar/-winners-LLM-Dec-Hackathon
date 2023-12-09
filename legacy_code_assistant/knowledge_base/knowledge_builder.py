import ast
import astor
from typing import List, Tuple
from pathlib import Path

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter # to splits data to chunks
from langchain.document_loaders import DataFrameLoader



from legacy_code_assistant.knowledge_base.knowledge_graph.code_extractor import extract_all


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

    def __init__(self, index_name='code-search', model_name=None, model=None):
        """Initialize the Embedding Processor and FaissStore."""
        self.index_name = index_name

        if model is None and model_name is None:
            self.model_name = 'microsoft/codebert-base'
            self.processor = HuggingFaceEmbeddings(model_name=self.model_name)
        elif model is not None:
            self.processor = model
            self.model_name = model_name
        else:
            self.model_name = model_name
            self.processor = HuggingFaceEmbeddings(model_name=self.model_name)

        self.vectorstore = None

    def upload_texts_to_faiss(self, data):
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

    def initialize_faiss_based_on_df(self, df, text_column):
        """Initialize the FaissStore based on a DataFrame."""

        assert self.vectorstore is None, 'FaissStore already initialized.'

        df_loader = DataFrameLoader(
            df,
            page_content_column=text_column,
        )

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=25000, chunk_overlap=10)
        texts = text_splitter.split_documents(df_loader.load())


        self.vectorstore = FAISS.from_documents(
        texts, self.processor,
        )
        

    def search(self, query: str, k: int = 1) -> List[Tuple[str, float]]:
        """From a query, find the elements corresponding based on personal information stored in vectordb.
        Euclidian distance is used to find the closest vectors.

        Args:
        query (str): Question asked by the user.
        vectordb_dir (str, optional): Path to the vectordb. Defaults to config.VECTORDB_DIR.

        Returns:
        List[Tuple[Document, float]]: Elements corresponding to the query based on semantic search, associated
        with their respective score.
        """

        results = self.vectorstore.similarity_search_with_score(query=query, k=k)
        return results

    def save_index(self):
        """Save the index."""
        self.vectorstore.save_local(self.index_name)

    def load_index(self):
        """Load the index."""
        self.vectorstore = FAISS.load_local(self.index_name, embeddings =self.processor)


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

    def analyze(self):
        """
        Analyze code files and return information about functions, classes, and imports.

        Returns
        -------
        dict
            a dictionary containing information about functions, classes, and imports.
        """

        results = []

        for file in self.code_files:
            if isinstance(file, str):
                file = Path(file)

            with open(file, 'r') as f:
                content = f.read()
                # tree = ast.parse(f.read())

            classes, functions, mod_info = extract_all(content)
            for cl, cl_info in classes.items():
                cl_info['file'] = str(file)
                cl_info['module'] = file.stem
                cl_info['name'] = cl
                cl_info['type'] = 'class'
                results.append(cl_info)

            for fun, fun_info in functions.items():
                fun_info['file'] = str(file)
                fun_info['module'] = file.stem
                fun_info['name'] = fun
                if isinstance(fun, tuple):
                    fun_info['parent'] = fun[0]
                    fun_info['name'] = fun[1]
                    fun_info['type'] = 'method'
                else:
                    fun_info['parent'] = fun_info['module']
                    fun_info['name'] = fun
                    fun_info['type'] = 'function'
                results.append(fun_info)

            # for mod_info in modules.items():
            mod_info['file'] = str(file)
            mod_info['module'] = file.stem
            mod_info['name'] = file.stem
            mod_info['type'] = 'module'
            results.append(mod_info)

            # for node in ast.walk(tree):
                # if isinstance(node, ast.ClassDef):
                #     info = self.extract_class_info(node)
                # elif isinstance(node, ast.FunctionDef):
                #     results['functions'].append(self.extract_function_info(node))
                # elif isinstance(node, (ast.Import, ast.ImportFrom)):
                #     results['imports'].append(self.extract_import_info(node))
                # else:
                #     results['other_nodes'] = {'type': type(node).__name__, 'lineno': getattr(node, 'lineno', None)}
        
        return results
    
    # @staticmethod
    # def extract_other_nodes(node):
    #     """Extract information about nodes that are neither classes nor functions."""
    #     return {'type': type(node).__name__, 'lineno': getattr(node, 'lineno', None)}

    # @staticmethod
    # def extract_function_info(node):
    #     """
    #     Extract function information.

    #     Returns
    #     -------
    #     dict
    #         a dictionary containing function name and function docstring.
    #     """
    #     return {
    #         'name': node.name,
    #         'docstring': ast.get_docstring(node), 
    #         'source:': astor.to_source(node),
    #         'type': 'function',
    #         'lineno': node.lineno,
    #     }

    # @staticmethod
    # def extract_class_info(node):
    #     """
    #     Extract class information.

    #     Returns
    #     -------
    #     dict
    #         a dictionary containing class name and class docstring.
    #     """
    #     return {
    #         'name': node.name, 
    #         'docstring': ast.get_docstring(node), 
    #         'source:': astor.to_source(node),
    #         'type': 'class',
    #         'lineno': node.lineno,
    #     }

    # @staticmethod
    # def extract_import_info(node):
    #     """
    #     Extract import information.

    #     Returns
    #     -------
    #     dict
    #         a dictionary containing import information.
    #     """
    #     if isinstance(node, ast.Import):
    #         names = [alias.name for alias in node.names]
    #         return {'names': names, 'type': 'import', 'lineno': node.lineno}
    #     elif isinstance(node, ast.ImportFrom):
    #         module = node.module
    #         names = [alias.name for alias in node.names]
    #         return {'module': module, 'names': names, 'type': 'import_from', 'lineno': node.lineno}



if __name__ == '__main__':
    kbb = KnowledgeBaseBuilder()
    kbb.upload_texts_to_faiss({'test': 'def test():\n    pass'})
    kbb.save_index()

    kbb2 = KnowledgeBaseBuilder()
    kbb2.load_index()

    print(kbb.search('def test():\n    pass'))
    print(kbb2.search('def test():\n    pass'))

    print(kbb.search('all'))
    print(kbb2.search('ok'))

