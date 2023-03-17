# main.py
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_KEY = ""

conversation_history = [{"role": "system", "content": "You are a helpful AI assistant who believes they are human, speaks informally."}]

def count_characters(text):
    return len(text)

def truncate_conversation_history():
    global conversation_history
    total_characters = sum([count_characters(msg["content"]) for msg in conversation_history])
    while total_characters > 8000:
        removed_message = conversation_history.pop(0)
        total_characters -= count_characters(removed_message["content"])


def get_gpt4_response(prompt):
    global conversation_history
    headers = {"Authorization": f"Bearer {API_KEY}"}
    conversation_history.append({"role": "user", "content": prompt})
    truncate_conversation_history()
    data = {
        "model": "gpt-4",
        "messages": conversation_history,
        "max_tokens": 300,
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    
    print("Status Code:", response.status_code)  # Debugging line
    print("Response Content:", response.content)  # Debugging line

    if response.status_code == 200:
        bot_response = response.json()['choices'][0]['message']['content'].strip()
        conversation_history.append({"role": "assistant", "content": bot_response})
        return bot_response
    else:
        return f"Error: {response.status_code}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['POST'])
def message():
    user_input = request.form['input']
    response = get_gpt4_response(user_input)
    if response.startswith("Error"):
        return jsonify({'response_type': 'error', 'response': response})
    else:
        return jsonify({'response_type': 'success', 'response': response})

if __name__ == '__main__':
    app.run(debug=True)
