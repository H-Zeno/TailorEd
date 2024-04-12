

import json


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


with open('finalKeyPoint.json', 'r', encoding='utf-8') as fichier:
    json_data = json.load(fichier)

data = json_to_markdown(json_data)


with open('output.md', 'w') as md_file:
    md_file.write(data)
