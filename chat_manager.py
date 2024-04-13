import os
from dotenv import load_dotenv
import langchain
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from assistant import *
load_dotenv()


class ChatManager:
    
    STATES = {
        "START": 0,
        "CHOOSE_TOPIC": 1,
        "DISCUSSING_TOPIC": 2,
        "END": 3,
    }
    
    
    def __init__(self) -> None:
        self.state = self.STATES["START"]
        self.discussion_topic = None
        self.topic_index = None
        self.relevant_data = None
        self.remaining_concepts = None
        
    
    # Concept and key points
    main_concepts = {'concept': 'Conquest of Jerusalem and its Aftermath', 'key_points': ['Brutal treatment of the Jewish and Christian populations in Jerusalem by the Crusaders', 'Capture of Jerusalem and the establishment of Baldwin as king', 'Defeat of the Egyptians under Al-Afdal Shahanshah in battles at Ramla and Jaffa']}

        
    def welcome_message(self, main_concepts: str, custom_message = "") -> str:
        print("START WELCOME CONVERSATION WITH TailorED")
        
        welcome_response = welcome_document_chain.invoke({
        "context": [Document(page_content=main_concepts, metadata={"source_type": "main concepts"})],
        "custom_message": [Document(page_content=custom_message, metadata={"source_type": "custom teacher message"})]
        })
        
        return welcome_response
    
    def choose_discussion_topic(self, chat_history: list, remaining_concepts: list):
        print("CHOOSE DISCUSSION TOPIC")
        # Choose the next discussion topic based on the recent conversational history
        
        topic_list = choose_topic_document_chain.invoke({
            "chat_history": chat_history,
            "context":  [Document(page_content=str(remaining_concepts), metadata={"source_type": "list of core concepts to cover"})]
            })
        
        try: 
            topic_response = topic_list[0]
            topic_index = topic_list[1]
            
        except Exception as e:
            print("Error: ", e)
            self.choose_discussion_topic(chat_history, remaining_concepts)

        return topic_response, topic_index
        
    
    def discussion_messages(self, user_input: str, chat_history: list,  main_concept: str, relevant_data: str) -> str:
        print("START DISCUSSION WITH TailorED (about a specific topic/concept)")
        response_dict = retrieval_chain.invoke({
            "chat_history": chat_history,
            "input": user_input,
            "current_main_concept": main_concept,	
            "relevant_data": relevant_data
            })
        response_text = response_dict.get('answer', 'No answer provided')  # Default message if 'answer' is missing
        return response_text