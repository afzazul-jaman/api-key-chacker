from flask import Flask, request, jsonify, send_from_directory
import concurrent.futures
from openai import OpenAI, OpenAIError

app = Flask(__name__, static_folder='static')

def test_key(key):
    client = OpenAI(api_key=key.strip())
    try:
        client.models.list()  # <-- Validate key here
        return (key, True)
    except OpenAIError as e:
        if hasattr(e, "status") and e.status == 401:
            return (key, False)
        return (key, False)
    except Exception:
        return (key, False)

@app.route('/check-keys', methods=['POST'])
def check_keys():
    data = request.json
    keys = data.get("keys", [])
    keys = keys[:500]  # Limit to 500 keys max

    valid_keys = []
    invalid_keys = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(test_key, keys))

    for key, valid in results:
        if valid:
            valid_keys.append(key)
        else:
            invalid_keys.append(key)

    return jsonify({"valid": valid_keys, "invalid": invalid_keys})

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
