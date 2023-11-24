from flask import Flask, render_template, request
from dotenv import load_dotenv
import openai
import os

load_dotenv()
app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
q = os.getenv("PROMPT")

def get_ai_response(question):
    prompt = question + q
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=1,
        max_tokens=1200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response['choices'][0]['text']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def process():
    question = request.form['question']
    assistant_content = get_ai_response(question)
    return render_template('index.html', question=question, assistant_content=assistant_content)

if __name__ == '__main__':
    app.run(debug=True)
