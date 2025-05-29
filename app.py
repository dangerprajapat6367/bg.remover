from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
import requests
import io
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

REMOVE_BG_API_KEY = 'pQc4wMu2jmkQ3QsoX31JbPbH'
REMOVE_BG_API_URL = 'https://api.remove.bg/v1.0/removebg'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/remove-background', methods=['POST'])
def remove_background():
    if 'image_file' not in request.files:
        return jsonify({'error': 'No image_file part in the request'}), 400

    image_file = request.files['image_file']
    if image_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        files = {'image_file': (image_file.filename, image_file.stream, image_file.mimetype)}
        data = {'size': 'auto'}
        headers = {'X-Api-Key': REMOVE_BG_API_KEY}

        response = requests.post(REMOVE_BG_API_URL, files=files, data=data, headers=headers)

        if response.status_code != 200:
            try:
                error_json = response.json()
                error_msg = error_json.get('errors', [{}])[0].get('title', 'Unknown error')
            except Exception:
                error_msg = f'Error from remove.bg API: status code {response.status_code}'
            return jsonify({'error': error_msg}), response.status_code

        return send_file(
            io.BytesIO(response.content),
            mimetype='image/png',
            as_attachment=True,
            download_name='no-background.png'
        )
    except Exception as e:
        return jsonify({'error': 'Internal server error: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
