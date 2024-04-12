import openai

with open('./key.txt', 'r') as file:
    key = file.read().strip()

# Now you can use the 'key' variable for further processing
openai.api_key = key

with open('./student_chat/prompts/init_prompt.txt', 'r') as prompts_file:
    prompts = prompts_file.read().strip()

with open('./data/keypoint_lists/kp_ww2.txt', 'r') as keypoints_file:
    keypoints = keypoints_file.read().strip()

#prompt = prompts + keypoints
prompt = "hi"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  
    messages=[{"role": "user", "content": prompt}], 
)

# Retrieve the generated response
generated_response = response.choices[0].text.strip()

print(generated_response)