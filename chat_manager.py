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
        "IDLE": 1,
        "DISCUSSING_TOPIC": 2,
        "END": 3,
    }
    
    
    
    def __init__(self) -> None:
        self.state = self.STATES["START"]
        self.discussion_topic = None
        
    
    # Concept and key points
    main_concepts = {'concept': 'Conquest of Jerusalem and its Aftermath', 'key_points': ['Brutal treatment of the Jewish and Christian populations in Jerusalem by the Crusaders', 'Capture of Jerusalem and the establishment of Baldwin as king', 'Defeat of the Egyptians under Al-Afdal Shahanshah in battles at Ramla and Jaffa']}

        
    def welcome_message(self, main_concepts: str, custom_message = "") -> str:
        print("START WELCOME CONVERSATION WITH TailorED")
        
        welcome_response = welcome_document_chain.invoke({
        "context": [Document(page_content=main_concepts, metadata={"source_type": "main concepts"})],
        "custom_message": [Document(page_content=custom_message, metadata={"source_type": "custom teacher message"})]
        })
        
        return welcome_response
        
    
    def discussion_messages(self, remaining_main_concepts: list, user_input: str, chat_history: list) -> str:
        print("START DISCUSSION WITH TailorED (about a specific topic/concept)")
        response_dict = retrieval_chain.invoke({
            "chat_history": chat_history,
            "input": user_input
            })
        response_text = response_dict.get('answer', 'No answer provided')  # Default message if 'answer' is missing
        return response_text