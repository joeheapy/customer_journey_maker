from flask import Flask, render_template, request, jsonify
import textwrap
import re
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up template directory
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# OpenAI client setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to capture detailed logs

#
def get_chatgpt_response(prompt):
    logging.debug("Sending prompt to OpenAI API: %s", prompt)
    try:
        response = client.chat.completions.create(
            model="gpt-4-0613",  # or whichever GPT-4 model you have access to
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        logging.debug("Received response from OpenAI API: %s", response)
        return response.choices[0].message.content
    except Exception as e:
        logging.error("Exception occurred while requesting OpenAI API: %s", e)
        raise

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

    # Log the received input
    logging.info("Received input: Business Proposition: %s, Target Customers: %s, Customer Scenario: %s, Persona Name: %s",
                 business_proposition, target_customers, customer_scenario, persona_name)

    # Main ChatGPT prompt

    input_prompt = f"You are a world-class customer experience designer. Design an innovative customer journey for a {target_customers} named {persona_name} interested in your {business_proposition} products and services. {persona_name} has {customer_scenario}. Write a narrative in steps from awareness of your products and services, the customer using your service, to the customer leaving your service and ongoing customer relationship management. Name this list of narrative steps {{journey_steps}}."

    try:
        chatgpt_response = get_chatgpt_response(input_prompt)
        logging.info("Successfully received response from OpenAI API.")
    except Exception as e:
        logging.error("Error while requesting OpenAI API: %s", e)
        return jsonify({"error": "Failed to generate journey"}), 500

    # Log the raw response for debugging
    logging.debug("Raw ChatGPT response: %s", chatgpt_response)

    journey_steps = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\Z)', chatgpt_response, re.DOTALL)
    journey_steps = [step.strip().split(':', 1) for step in journey_steps]
    journey_steps = [(name.strip(), wrap_text(desc.strip(), width=20) if len(desc) > 1 else "") for name, desc in journey_steps]

    # Log the processed journey steps
    logging.debug("Processed journey steps: %s", journey_steps)

    return jsonify(journey_steps)

if __name__ == '__main__':
    app.run()
    # This is used when running locally only. When deploying to Google Cloud Run,
    # a webserver process such as Gunicorn will serve the app.
    #port = int(os.environ.get("PORT", 8080))
    #app.run(debug=False, host='0.0.0.0', port=port)
