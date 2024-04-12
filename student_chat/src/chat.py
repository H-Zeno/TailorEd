import openai

with open('./key.txt', 'r') as file:
    key = file.read().strip()

# Now you can use the 'key' variable for further processing
openai.api_key = key