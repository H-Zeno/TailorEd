import os
import assistant
from chat_manager import ChatManager
from langchain_core.messages import HumanMessage, AIMessage



ChatManager = ChatManager()

chat_history = []

def main():
    print("Start conversation with TailorED (type 'quit' to exit):")
    
    while True:
        if not ChatManager.state == ChatManager.STATES["START"]:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                break
        
        if ChatManager.state == ChatManager.STATES["START"]:
            response_text = ChatManager.welcome_message(main_concepts="We are talking about the history of Crusades")
            print('response text', response_text)
            ChatManager.state = ChatManager.STATES["IDLE"]
            
            chat_history.append(AIMessage(content=response_text))
        
        if ChatManager.state == ChatManager.STATES["IDLE"]:
            # set the next discussion topic (choose from a list of strings of topics) that matches the best with the recent conversational history and question of the student
            
        
            pass 
            
            
        if ChatManager.state == ChatManager.STATES["DISCUSSING_TOPIC"]:
            response_text = ChatManager.discussion_messages(main_concept=ChatManager.discussion_topic, relevant_data=ChatManager.relevant_data, user_input=user_input, chat_history=chat_history)
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=response_text))

            if response_text[-16:] == "FULLY_UNDERSTOOD":
                ChatManager.state = ChatManager.STATES["IDLE"]
            else:
                pass
        
        
    
        print("Katie:", response_text)
        
    

if __name__ == "__main__":
    main()