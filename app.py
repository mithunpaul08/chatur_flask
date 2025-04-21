from flask import Flask, request, jsonify
import os
from chains.llm_proxy import build_llm_proxy

app = Flask(__name__)

llm_url = 'https://llm-api.cyverse.ai'
api_key = os.environ.get('API_KEY')
OPENAI_API_KEY = os.environ.get('AIAI_API_KEY')

@app.route('/invoke', methods=['GET', 'POST'])
def invoke():
    if request.method == 'GET':
        prompt = request.args.get("prompt")
        model_name = request.args.get("model")
    else:
        data = request.json
        prompt = data.get("prompt")
        model_name = data.get("model")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    if not model_name:
        return jsonify({"error": "No model name provided"}), 400

    try:
        # Build the LLM proxy with the specified model name
        llm = build_llm_proxy(
            model=model_name,
            url=llm_url,
            engine="OpenAI",
            temperature=0.9,
            api_key=OPENAI_API_KEY,
        )

        response = llm.invoke(prompt)
        return jsonify({"response": str(response.content)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)