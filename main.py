import os
import json
import assistant
from chat_manager import ChatManager
from langchain_core.messages import HumanMessage, AIMessage





chat_history = []
main_concepts = []

# Add main concepts to the Chat Manager from the JSON file
with open('Content/mathematicScriptkeyPoint.json', 'r') as file:
    main_concepts_JSON = json.load(file)
    
# Iterate over each major section and collect subtitles
for main_concept, relevant_data in main_concepts_JSON.items():
    main_concepts.append(main_concept)

ChatManager = ChatManager()
ChatManager.remaining_concepts = main_concepts

def main():
    print("Start conversation with TailorED (type 'quit' to exit):")
    
    while True:
        if not ChatManager.state == ChatManager.STATES["START"]:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                print("Thank you for practicing together! Let's continue were we left off next time.")
                break
        # START
        if ChatManager.state == ChatManager.STATES["START"]:
            response_text = ChatManager.welcome_message(main_concepts=str(main_concepts))
            #print('response text', response_text)
            ChatManager.state = ChatManager.STATES["CHOOSE_TOPIC"]
            chat_history.append(AIMessage(content=response_text))
            print("Katie:", response_text)
            continue
        
        # CHOOSE TOPIC
        if ChatManager.state == ChatManager.STATES["CHOOSE_TOPIC"]:
            if ChatManager.remaining_concepts == []:
                ChatManager.state = ChatManager.STATES["END"]
                continue
            if ChatManager.discussion_topic is not None and ChatManager.remaining_concepts is not None:
                # remove the last discussed topic from the list of remaining topics
                ChatManager.remaining_concepts.pop(ChatManager.topic_index)
            topic, topic_index = ChatManager.choose_discussion_topic(chat_history=chat_history, remaining_concepts=ChatManager.remaining_concepts)
            ChatManager.discussion_topic = topic
            ChatManager.topic_index = topic_index
            ChatManager.state = ChatManager.STATES["DISCUSSING_TOPIC"]
            print("Katie:", response_text)
            continue
        
        # DISCUSSING TOPIC
        if ChatManager.state == ChatManager.STATES["DISCUSSING_TOPIC"]:
            response_text = ChatManager.discussion_messages(main_concept=ChatManager.discussion_topic, relevant_data=ChatManager.relevant_data, user_input=user_input, chat_history=chat_history)
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=response_text))

            if response_text[-16:] == "FULLY_UNDERSTOOD":
                ChatManager.state = ChatManager.STATES["CHOOSE_TOPIC"]
                response_text = response_text[:-16]
            else:
                pass
            print("Katie:", response_text)
            
        
        # END
        if ChatManager.state == ChatManager.STATES["END"]:
            print("Thank you for practicing together! Let's continue were we left off next time.")
            break
        
        
    

if __name__ == "__main__":
    main()