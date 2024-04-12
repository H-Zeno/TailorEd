
import json
import os
import re
from openai import OpenAI
from langchain_community.document_loaders import TextLoader
from semantic_text_splitter import TextSplitter


def json_to_markdown(json_data):
    markdown_text = ""
    # Iterate through each key (topic) and its dictionary
    for topic, details in json_data.items():
        # Add a heading with the topic name
        markdown_text += f"## <{topic} >\n"
        # Iterate through each sub-topic
        for sub_topic, points in details.items():
            # Add a bold sub-topic
            markdown_text += f"- **<{sub_topic} >**:\n"
            # List all points under this sub-topic
            for point in points:
                markdown_text += f"   - {point}\n"
        # Add an extra newline for spacing between topics
        markdown_text += "\n"
    return markdown_text


courseName = "mathematicScript"

loader = TextLoader(courseName + ".txt")
documents = loader.load()
# print(documents[0].page_content)

max_characters = 1000
splitter = TextSplitter()

chunks = splitter.chunks(
    str(documents[0].page_content), chunk_capacity=(4000, 7000))

print(len(chunks))

for chunk in chunks:
    with open('exemple.txt', 'a') as fichier:
        fichier.write(chunk)
        fichier.write('\n\n')


summary = []
questions = []
for i in range(len(chunks)):
    prompt_request = "Make a summary of the following lecture transcript excerpt. Format your response in markdown:" + str(
        chunks[i])

    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt_request
            }
        ]
    )
    summary.append(completion.choices[0].message.content)

    prompt_request = "Make a dictionnary of the 10-15 most important informations. The format of your answer should be : {\"description/questions\" : \"answer\", \"date of ...\" : \"1978-1980\"}, the answer and the description/question shouldn't be too long. " + str(
        chunks[i])
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt_request
            }
        ]
    )
    questions.append(completion.choices[0].message.content)

with open('summary.txt', 'a') as fichier:
    fichier.write(str(summary))

with open('questions.txt', 'a') as fichier:
    fichier.write(str(questions))


data = []
for i in range(len(summary)):
    data.append(f"{summary[i]}, {questions[i]}")

print(data)
with open("prompt3.txt", "r") as f:
    summary_prompt = f.read()


prompt_request = summary_prompt + str(summary)

client = OpenAI()
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": prompt_request
        }
    ]
)

print(completion.choices[0].message.content)

with open('text.txt', 'w') as fichier:
    fichier.write(str(completion.choices[0].message.content))

with open('text.txt', 'r') as f:
    data = json.load(f)

with open(courseName + 'keyPoint' + '.json', 'w') as fichier:
    json.dump(data, fichier, indent=4)


with open(courseName + 'keyPoint' + '.json', 'r', encoding='utf-8') as fichier:
    json_data = json.load(fichier)

data = json_to_markdown(json_data)


with open(courseName + 'keyPoint' + '.md', 'w') as md_file:
    md_file.write(data)
