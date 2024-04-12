import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_ai21 import AI21SemanticTextSplitter



load_dotenv()

llm = ChatOpenAI(api_key = os.getenv("OPENAI_API_KEY"))
embeddings = OpenAIEmbeddings()

db = FAISS.load_local("Vector_DB/lecture_crusades", embeddings, allow_dangerous_deserialization=True)

chat_history = [HumanMessage(content="Do you know something about Syria?"), AIMessage(content="Yes!")]

# create the retrieval chain
retriever = db.as_retriever(search_kwargs={"score_threshold": 0.5}) # also possible: best k

# Retrieve relevant documents (in the database) based on the conversation history
retrieve_query_prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ("user", "Given the above conversation, generate a search query to look up to get information relevant to the conversation.")
])
retrieve_context_chain = create_history_aware_retriever(llm, retriever, retrieve_query_prompt)

# Answer the user's questions based on the context of the conversation
prompt_answer_with_context = ChatPromptTemplate.from_messages([
    ("system", "Answer the user's questions based on the below context:\n\n{context}"), 
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
])
document_chain = create_stuff_documents_chain(llm, prompt_answer_with_context) # a chain with specified documents as input

retrieval_chain = create_retrieval_chain(retrieve_context_chain, document_chain)


output = retrieval_chain.invoke({
    "chat_history": chat_history,
    "input": "What happend in Syria during the Crusades? Could you provide me with a summary?"
})

print(output)   



""" 

# create history aware (past conversation) and content aware (transcripts) retriever
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the user's questions based on the below context:\n\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
])



retrieval_chain = create_retrieval_chain(retriever_chain, document_chain)

 """









""" output_parser = StrOutputParser()


chain = prompt | llm | output_parser

output = chain.invoke({"input": "how can langsmith help with testing?"})

print(output) """



""" print(f"{len(docs)} relavant documents have been found")
for doc in docs:
    print(f"type: {doc.metadata['source_type']}")
    print(f"text: {doc.page_content}")
    print("====")
 """
    



