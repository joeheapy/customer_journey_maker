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

# Global variables
source_prompt = "Do not hyphenate words.Do not use semicolons.1. Define journey steps: As a product manager, redesign the customer experience for 'target_customers' interested in your 'business_proposition' products and services. List the steps in the 'customer_mission', from awareness of the company to ending the customer relationship. Include ongoing relationship management. Now rewrite the steps to define a world class experience for your customers. Name this set of steps {{journey_steps}}."

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

    input_prompt = f"{source_prompt} I am a Customer Experience Manager for {business_proposition}. My service targets {target_customers}. I need define the customer journey steps for our service, from initial awareness to post-purchase support, ongoing relationships and leaving, ensuring that each stage is detailed and customer-centric. I want to define the journey for customers {customer_scenario}. The persona name for this journey is {persona_name}."

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
