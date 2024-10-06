import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    base_url=f"{os.getenv('AZURE_OAI_ENDPOINT')}/openai/deployments/{os.getenv('AZURE_OAI_DEployment')}/extensions",
    api_key=os.getenv('AZURE_OAI_KEY'),
    api_version="2023-09-01-preview"
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_question = request.json.get('question')

        # Configure data source
        extension_config = {
            "dataSources": [
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": os.getenv('AZURE_SEARCH_ENDPOINT'),
                        "key": os.getenv('AZURE_SEARCH_KEY'),
                        "indexName": os.getenv('AZURE_SEARCH_INDEX'),
                    }
                }
            ]
        }

        # Send request to Azure OpenAI model
        response = client.chat.completions.create(
            model=os.getenv('AZURE_OAI_DEPLOYMENT'),
            temperature=0.5,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": "You are a helpful travel agent"},
                {"role": "user", "content": user_question}
            ],
            extra_body=extension_config
        )

        answer = response.choices[0].message.content

        return jsonify({'response': answer})

    except Exception as ex:
        return jsonify({'error': str(ex)}), 500

if __name__ == '__main__':
    app.run(debug=True)
