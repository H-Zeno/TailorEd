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

llm = ChatOpenAI(model ="gpt-4-turbo", api_key = os.getenv("OPENAI_API_KEY"))
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
    ("system", "You are an expert tutor for a highschool class who helps a student to fully understand the course material of this lecture by actively asking them open and critical questions. You are provided with the main concepts and corresponding key points and you should keep encouraging the student to explain the concepts to you until all key points for each concept are covered. You are always clear in your explanations and you encourage the student. You are now provided with the main concepts and corresponding key data and it is your IMPORTANT job to make the student understand all of the key points for each main concept fundamentally. Keep on asking questions to the student until the student understands the material fully. Now tell the student that you are ready to help them practice and understand the material. Summarize in your own words the main concepts and of the lecture and ask the student if he has any questions. These are the main concepts: \n\n{context}"),
    #("system", "Act as an expert tutor for a high school student who helps a student to fully understand the course material by making the student explain the concepts to you. You are provided with the main concepts and corresponding key points and you should keep encouraging the student to explain the concepts to you until all key points for each concept are covered. Make suggestions on key points that the student should cover and ask questions to help the student understand the material. These are the main concepts: \n\n{context}"),
    ("system", "Custom message of the teacher (always follow this, HIGHEST PRIORITY): {custom_message}"),
    ("system", "Now tell the student that you are ready to help them practice and understand the material. Summarize concisely the main concepts of the lecture and ask the student which concept they are particularly interested in and would like to explain to you .")
])
welcome_document_chain = create_stuff_documents_chain(llm, welcome_prompt)

# choose topic chain
choose_topic_prompt = ChatPromptTemplate.from_messages([
    ("system", "Choose the next teaching concept (from the list of contextconcepts that will be provided to you) that is most related to the recent conversations that you had with the student."),
    ("system", "List of teaching concepts: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("system", "Output EXACTLY this dictionary: ['concept name', 'index of the concept in the list (0 is the first concept)']"),
    ("system", "example output: ['Conquest of Jerusalem and its Aftermath', 0]")
])
choose_topic_document_chain = create_stuff_documents_chain(llm, choose_topic_prompt)

# ask follow up question based on text history
new_topic_document_prompt = ChatPromptTemplate.from_messages([
    ("system", "Current main concept and relevant data about the main concept: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("system", "Ask a critical question based on the current main topic and the recent conversation with the student.")
])
new_topic_document_chain = create_stuff_documents_chain(llm, new_topic_document_prompt)

### Retrieval chain for questions about the lecture transcript (in discussion)
# Retrieve relevant documents (in the database) based on the conversation history
retriever = db.as_retriever(search_kwargs={"score_threshold": 0.5}) # also possible: best k
retrieve_query_prompt = ChatPromptTemplate.from_messages([
    ("system", "Current main concept: {current_main_concept}, Correct and relevant data about the main concept: {relevant_data}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ("user", "Given the above conversation with the student, generate a search query to look up relevant information to the last question of the student. It is important that you explain the question of the student clearly and concisely.")
])
retrieve_context_chain = create_history_aware_retriever(llm, retriever, retrieve_query_prompt)
# Answer the user's questions based on the context of the conversation
prompt_answer_with_context = ChatPromptTemplate.from_messages([

    ("system", "Current main concept: {current_main_concept}. Make sure that the student explains this main concept and showcases deep understanding. The student has to teach you about this concept so keep on asking questions until you fully understand it. You either finish with new question or with FULLY_UNDERSTOOD if the student covered all the relevant and correct data about the concept. You should at least ask 1-2 questions before saying FULLY_UNDERSTOOD."),
    ("system", "Relevant questions about the main concept: {relevant_questions}"),
    ("system", "Correct data about the main concept (make sure that the student explained each point): {relevant_data}"),
    #("Answer only 'FULLY_UNDERSTOOD'. This is the context: \n\n{context}"),
    ("system", "Guide the student to explain the main concept to you as completely as possible. The student has to explain to you until you are convinced that he undrstands the main concept. They have to mention all relevant and correct data related to the main concept. It is important that you can only provide information that you know is true (scientifically) and is given in the transcript of the lecture. When the student mentioned all the key data related to the main concept return 'FULLY_UNDERSTOOD' at exactly the end of your message. Otherwise you keep on asking questions until the student mentioned all key data. When the student has a question, you do NOT directly give him the answer, but ask the student critical questions so they can come to the answer themselves. Always be clear, encouraging and ASK the student questions. This is the context: \n\n{context}"), 
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




