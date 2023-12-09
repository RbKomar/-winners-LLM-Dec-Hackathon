from pathlib import Path
import yaml
import os
import pandas as pd
import sys
# from legacy_code_assistant.knowledge_base.description_generator import CodeConditionedGenerator
# from legacy_code_assistant.knowledge_base.knowledge_builder import KnowledgeBaseBuilder
# from legacy_code_assistant.knowledge_base.knowledge_builder import CodeAnalyzer
from langchain.embeddings import AzureOpenAIEmbeddings

from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.vectorstores import FAISS

with open('../notebooks/credentials.yaml', "r") as f:
    credentials = yaml.load(f, Loader=yaml.FullLoader)
os.environ["AZURE_OPENAI_ENDPOINT"] = credentials['AZURE_OPENAI_ENDPOINT']
os.environ["AZURE_OPENAI_API_KEY"] = credentials['AZURE_OPENAI_API_KEY']


#   def getFunctionsDataFrame():
#       path = Path() / '..' / '..' / 'dziwne' / 'Django-School-Management-System' 
#       paths = list(path.rglob('**/*.py'))
#       ca = CodeAnalyzer(paths)
#       results = ca.analyze()
#       df = pd.DataFrame(results)
#       print("pozyskalem baze danych")
#       return df



class pipeProcess:
  def __init__(self):
      self.model = AzureChatOpenAI(
            openai_api_version="2023-05-15",
            azure_deployment=credentials['Deployment_completion'],
        )
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=credentials['Deployment_embeddings'],
            openai_api_version="2023-05-15",
        )
        self.df = pd.read_csv('generated_docstrings.csv')

  def analyzePipe(self):
      print("Wchodzę w pipe analizy, Wpisz swój prompt do chatu")
      prompt_template = """
          Uzyskujesz zapytanie, w którym podana jest jedna z wymienionych kategorii: analiza kodu
          , dodawanie funkcji, modyfikacja funkcji, inne. 
          Kategoria: {user_input}
          # """
      chat_prompt_template = ChatPromptTemplate.from_template(prompt_template)
      user_input = input()
      prompt_to_go = chat_prompt_template.format_prompt(user_input=user_input)
      print("Wejście do zapytania: ",prompt_to_go)

      # result = model(prompt_to_go.to_messages()).content
      # print("result",result)

  def addPipe(self):
      print("Wchodzę w pipe dodawania, Wpisz swój prompt do chatu")
      prompt_template = """
      Uzyskujesz zapytanie, w którym podana jest jedna z wymienionych kategorii: analiza kodu
      , dodawanie funkcji, modyfikacja funkcji, inne. 
      Kategoria: {user_input}
      # """
      chat_prompt_template = ChatPromptTemplate.from_template(prompt_template)
      user_input = input()
      prompt_to_go = chat_prompt_template.format_prompt(user_input=user_input)
      print("Wejście do zapytania: ",prompt_to_go)

  def modifyPipe(self):
      print("Wchodzę w pipe modyfikacji, Wpisz swój prompt do chatu")
      prompt = input()
      # prompt = ChatPromptTemplate.from_template(prompt)
      # result = model(prompt.to_messages()).content
      # print("result",result)

  def otherPipe(self):
      print("Wchodzę w pipe inne, Wpisz swój prompt do chatu") 
      prompt = input()
      # prompt = ChatPromptTemplate.from_template(prompt)
      # result = model(prompt.to_messages()).content
      # print("result",result)

  def getChain(self, query, k=10):
      print("Wchodzę w semantic search, Wpisz swój prompt do chatu")
      kbb_docs = KnowledgeBaseBuilder(index_name='docstring_based_index', model=self.embeddings)
      kbb_docs.initialize_faiss_based_on_df(self.df, text_column='generated_docstring')
      retriever = kbb_docs.get_retriever()

      template = """Answer the question based only on the following context:
     {context} Question: {question}"""
      prompt = ChatPromptTemplate.from_template(template)
      chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
     )
      return chain




  def startPipe(self):      
      print("Wybierz jedną z mozliwych kategorii: 1: Analiza, 2: Dodanie, 3: Modyfikacja, 4: Inne. Wpisz numer kategorii: ")
      category = input()
      print("Wybrana kategoria to "+ category) 
      if (category == "1"):
          self.analyzePipe()
      elif (category == "2"):
          self.addPipe()
      elif (category == "3"):
          self.modifyPipe()
      elif (category == "4"):
          self.otherPipe()

pipe = pipeProcess()
pipe.startPipe()
