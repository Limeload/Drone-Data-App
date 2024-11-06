import json
import openai
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

DATASET_DIR = os.path.join(os.path.dirname(__file__), 'datasets')

def load_dataset(filename):
    """
    Load the specified JSON dataset and convert it to a string context for ChatGPT.
    """
    dataset_path = os.path.join(DATASET_DIR, filename)
    try:
        with open(dataset_path) as f:
            drone_data = json.load(f)
        dataset_context = "\n".join([
            f"Image ID: {item['image_id']}, Altitude: {item['altitude_m']} m, Battery Level: {item['battery_level_pct']}%, Timestamp: {item['timestamp']}, Tags: {', '.join(item['image_tags'])}"
            for item in drone_data
        ])
        return dataset_context
    except Exception as e:
        return None, str(e)

def get_chatgpt_response(question, dataset_context):
    """
    Send the user query and dataset context to ChatGPT, and retrieve the response.
    """
    prompt = f"The following is a dataset of drone images:\n\n{dataset_context}\n\nBased on this data, answer the following question: {question}"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        temperature=0
    )
    return response['choices'][0]['text'].strip()

@app.route('/api/datasets', methods=['GET'])
def list_datasets():
    """
    List all JSON dataset files available in the dataset directory.
    """
    datasets = [f for f in os.listdir(DATASET_DIR) if f.endswith('.json')]
    return jsonify({"datasets": datasets})

@app.route('/api/dataset/<filename>', methods=['GET'])
def get_dataset(filename):
    """
    Fetch and serve a specific dataset file by name.
    """
    try:
        if filename in os.listdir(DATASET_DIR):
            return send_from_directory(DATASET_DIR, filename)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query():
    """
    Endpoint to process a query using a specified dataset and retrieve ChatGPT's response.
    """
    data = request.json
    question = data.get("question")
    filename = data.get("filename")

    if not question or not filename:
        return jsonify({"error": "Both 'question' and 'filename' are required"}), 400

    dataset_context, error = load_dataset(filename)
    if error:
        return jsonify({"error": f"Failed to load dataset: {error}"}), 500

    response_text = get_chatgpt_response(question, dataset_context)
    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(port=5000)
