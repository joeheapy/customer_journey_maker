from flask import Flask, render_template, request, jsonify
import textwrap
import re
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up template directory
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# OpenAI client setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def get_chatgpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4-0613",  # or whichever GPT-4 model you have access to
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def wrap_text(text, width):
    return '\n'.join(textwrap.wrap(text, width=width))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    business_proposition = request.form['business_proposition']
    target_customers = request.form['target_customers']
    customer_scenario = request.form['customer_scenario']
    persona_name = request.form['persona_name']

    # Main ChatGPT prompt

    input_prompt = f"Do not hyphenate words. Do not use semicolons. Write a customer journey story in steps. As a world-class customer experience designer, redesign an innovative customer journey for an {target_customers} named {persona_name} interested in your {business_proposition} products and services. Write the narraive steps for {persona_name} when they {customer_scenario}, from awareness of the company to leaving your service and ongoing relationship management. Name this set of steps {{journey_steps}}."

    chatgpt_response = get_chatgpt_response(input_prompt)

    journey_steps = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\Z)', chatgpt_response, re.DOTALL)
    journey_steps = [step.strip().split(':', 1) for step in journey_steps]
    journey_steps = [(name.strip(), wrap_text(desc.strip(), width=20) if len(desc) > 1 else "") for name, desc in journey_steps]

    return jsonify(journey_steps)

if __name__ == '__main__':
    app.run()
    # This is used when running locally only. When deploying to Google Cloud Run,
    # a webserver process such as Gunicorn will serve the app.
    #port = int(os.environ.get("PORT", 8080))
    #app.run(debug=False, host='0.0.0.0', port=port)
