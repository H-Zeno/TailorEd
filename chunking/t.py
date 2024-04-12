
import json
import os
import re
from openai import OpenAI
from langchain_community.document_loaders import TextLoader
from semantic_text_splitter import TextSplitter


with open("questions.txt", "r") as f:
    questions = f.read()
with open("summary.txt", "r") as f:
    summary = f.read()
with open("prompt3.txt", "r") as f:
    summary_prompt = f.read()

prompt_request = summary_prompt + summary

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

with open('text.json', 'w') as fichier:
    json.dump(data, fichier, indent=4)
