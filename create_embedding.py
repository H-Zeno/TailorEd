import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_ai21 import AI21SemanticTextSplitter

load_dotenv()

# load models
llm = ChatOpenAI(api_key = os.getenv("OPENAI_API_KEY"))
embeddings = OpenAIEmbeddings()
semantic_text_splitter = AI21SemanticTextSplitter()


# load text content
""" loader = TextLoader(".\Content\Oxford_English_Dictionary.txt", encoding="utf-8")
documents = loader.load() """
text_file = open("Content\lecture_crusades.txt", "r", encoding="utf-8")
text = text_file.read()
text_file.close()

print(len(text))

# split the text semantically into documents
docs = semantic_text_splitter.split_text_to_documents(text) # idea: we can create documents with the metadata of the time in the lecture that the specific sentence arrized
embeddings = OpenAIEmbeddings()
vector_db = FAISS.from_documents(docs, embeddings)

print(f"The text has been split into {len(docs)} Documents.")
for doc in docs:
    print(f"type: {doc.metadata['source_type']}")
    print(f"text: {doc.page_content}")
    print("====")

vector_db.save_local("Vector_DB\lecture_crusades")




