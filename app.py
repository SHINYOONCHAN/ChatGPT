from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
q = os.getenv("PROMPT")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True, encoding='utf-8')


def create_chat_completion(messages, model="gpt-3.5-turbo", stream=True):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    payload = {
        "model": model,
        "messages": messages,
        "stream": stream
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), stream=True)
    for line in response.iter_lines():
        if not line:
            continue
    
        data = line.decode('utf-8')
    
        if "[DONE]" in data:
            break
    
        try:
            json_data = json.loads(data[6:].strip())
            choices = json_data.get('choices', [])
        
            if choices:
                delta = choices[0].get('delta', {})
                content = delta.get('content', '')
            
                if content:
                    socketio.emit('assistant_response', {'response': content})
            elif json_data.get('finish_reason') == 'stop':
                break
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('ask_question')
def handle_question(data):
    user_question = data['question']
    system_message = {"role": "system", "content": "You are a helpful assistant."}
    user_message = {"role": "user", "content": user_question + q}
    messages = [system_message, user_message]
    create_chat_completion(messages)

if __name__ == '__main__':
    socketio.run(app)
