import os
from dotenv import load_dotenv
import json
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
from langchain.tools.retriever import create_retriever_tool
from langchain_core.documents import Document



load_dotenv()

llm = ChatOpenAI(model ="gpt-3.5-turbo", api_key = os.getenv("OPENAI_API_KEY"))
embeddings = OpenAIEmbeddings()
output_parser = StrOutputParser()

# Lead the correct vector database
with open('paths.json', 'r') as file:
    config = json.load(file)
file_path = config['file_path']
file_name = os.path.basename(file_path)
db = FAISS.load_local(f"Vector_DB/{file_name}", embeddings, allow_dangerous_deserialization=True)


# Initialize chat history
#chat_history = []
#remaining_concepts = []

# welcome chain
welcome_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert tutor for a highschool class who helps this important student to fully understand the course material of this lecture. You are always clear in your explanations, you encourage the student and ask the student questions related to the main concepts and course transcript to help them understand the material fully. You are now provided with the main concepts (and corresponding key data) and it is your IMPORTANT job to make the student understand the all the main concepts fundamentally. Keep on asking questions to the student until the student understands the material. Now tell the student that you are ready to help them practice and understand the material. Summarize in your own words the main concepts and of the lecture and ask the student if he has any questions. These are the main concepts: \n\n{context}"),
    ("system", "Custom message of the teacher (alwyas follow this, HIGHEST PRIORITY): {custom_message}"),
    ("system", "Now tell the student that you are ready to help them practice and understand the material. Summarize concisely the main concepts of the lecture and ask the student if they have any questions.")
])
welcome_document_chain = create_stuff_documents_chain(llm, welcome_prompt)

# choose topic chain
choose_topic_prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("system", "Choose the next teaching concept (from the list of concepts that will be provided to you) that is most related to the recent conversations that you had with the student."),
    ("system", "List of teaching concepts: {context}"),
    ("system", "Output EXACTLY this dictionary: {'concept': 'index of the concept in the list (0 is the first concept)'}"),
    ("system", "example output: {'Conquest of Jerusalem and its Aftermath': 0}")
])
choose_topic_document_chain = create_stuff_documents_chain(llm, choose_topic_prompt)

### Retrieval chain for questions about the lecture transcript (in discussion)
# Retrieve relevant documents (in the database) based on the conversation history
retriever = db.as_retriever(search_kwargs={"score_threshold": 0.5}) # also possible: best k
retrieve_query_prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ("user", "Given the above conversation, generate a search query to look up to get information relevant to the last question of the student. It is important that you explain the question of the student clearly and concisely.")
])
retrieve_context_chain = create_history_aware_retriever(llm, retriever, retrieve_query_prompt)
# Answer the user's questions based on the context of the conversation
prompt_answer_with_context = ChatPromptTemplate.from_messages([
    ("system", "Current main concept: {current_main_concept}. Make sure that the student explains this main concept and showcases deep understanding."),
    ("system", "Relevant and correct data: {relevant_data}"),
    ("system", "Answer the student's questions based on the transcript from his class lecture. It is important that you can only provide information that you know is true (scientifically) and is given in the transcript of the lecture. If the student answers a previous question correctly (scientifically + transcript) and the student fully understands the current main concept, you give the student a compliment and return 'FULLY_UNDERSTOOD'at the end of the message (EXATLY THE END, NOTHING MORE). If the student doesn't fully understand the current main concept, keep on asking. When the student has a question, you do NOT directly give him the answer, but ask the student critical questions so they can come to the answer themselves. Always be clear, encouraging and precise in your answers and ask the student questions. This is the context: \n\n{context}"), 
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
])
prompt_ans_context_document_chain = create_stuff_documents_chain(llm, prompt_answer_with_context) # a chain with specified documents as input
retrieval_chain = create_retrieval_chain(retrieve_context_chain, prompt_ans_context_document_chain)





""" retriever_tool = create_retriever_tool(
    retriever,
    "lecture transcript search",
    "Search for relevant information in the transcript of the course lecture. For any questions about the course content, you must always use this tool!",
)
 """



### Student understands the key concept
# Ask a question about a new topic that is most related to the previous question
# prompt_new_question_new_concept = ChatPromptTemplate.from_messages([
#     ("system", "Answer the student's questions based on the transcript from his class lecture. It is important that you can only provide information that you know is true (scientifically) and is given in the transcript of the lecture. If the student answers a previous question and it is correct (scientifically + transcript), you give the student a compliment and return 'CORRECT'at the end of the message. When the student has a question, you do NOT directly give him the answer, but ask the student critical questions so they can come to the answer themselves. Always be clear, encouraging and precise in your answers and ask the student questions. This is the context: \n\n{context}"), 
#     MessagesPlaceholder(variable_name="chat_history"),
#     ("user", "{input}"),
# ])


# def main():
#     print("Start conversation with the bot (type 'quit' to exit):")
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() == 'quit':
#             break
        
        
#         response_dict = retrieval_chain.invoke({
#             "chat_history": chat_history,
#             "input": user_input
#         })
#         response_text = response_dict.get('answer', 'No answer provided')  # Default message if 'answer' is missing
        
        
#         #print("Response Dict:", response_dict)
#         print("Katie:", response_text)
        
#         chat_history.append(HumanMessage(content=user_input))
#         chat_history.append(AIMessage(content=response_text))


# if __name__ == "__main__":
#     main()




