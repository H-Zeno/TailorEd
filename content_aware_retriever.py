import os
from dotenv import load_dotenv
import langchain
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

langchain.verbose = True

llm = ChatOpenAI(api_key = os.getenv("OPENAI_API_KEY"))
embeddings = OpenAIEmbeddings()

db = FAISS.load_local("Vector_DB/lecture_crusades", embeddings, allow_dangerous_deserialization=True)


# Initialize chat history
chat_history = [] 

# innitialize retrieval chain
retriever = db.as_retriever(search_kwargs={"score_threshold": 0.5}) # also possible: best k

# Retrieve relevant documents (in the database) based on the conversation history
retrieve_query_prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ("user", "Given the above conversation, generate a search query to look up to get information relevant to the last question of the student. It is important that you explain the question of the student clearly and concisely.")
])
retrieve_context_chain = create_history_aware_retriever(llm, retriever, retrieve_query_prompt)


# Answer the user's questions based on the context of the conversation
prompt_answer_with_context = ChatPromptTemplate.from_messages([
    ("system", "Answer the student's questions based on the transcript from his class lecture. It is important that you can only provide information that you know is true (scientifically) and is given in the transcript of the lecture. If the student answers a previous question and it is correct (scientifically + transcript), you give the student a compliment and return 'CORRECT'at the end of the message. When the student has a question, you do NOT directly give him the answer, but ask the student critical questions so they can come to the answer themselves. Always be clear, encouraging and precise in your answers and ask the student questions. This is the context: \n\n{context}"), 
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
])
document_chain = create_stuff_documents_chain(llm, prompt_answer_with_context) # a chain with specified documents as input
retrieval_chain = create_retrieval_chain(retrieve_context_chain, document_chain)




def main():
    print("Start conversation with the bot (type 'quit' to exit):")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        
        
        response_dict = retrieval_chain.invoke({
            "chat_history": chat_history,
            "input": user_input
        })
        response_text = response_dict.get('answer', 'No answer provided')  # Default message if 'answer' is missing
        
        
        #print("Response Dict:", response_dict)
        print("Katie:", response_text)
        
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response_text))


if __name__ == "__main__":
    main()




