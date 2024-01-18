from flask import Flask, render_template, request
import re
import json
import base64

app = Flask(__name__)

def decode_base64(data, altchars=b'-_'):
    try:
        data = bytes(data, 'utf-8')
        data = data.replace(b'-', b'+').replace(b'_', b'/')
        data = re.sub(rb'[^a-zA-Z0-9+/=]', b'', data)
        padding_needed = 4 - (len(data) % 4)
        if padding_needed < 4:
            data += b'=' * padding_needed
        decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')  # Decode bytes to string
        return decoded_data
    except Exception as e:
        return None

def extract_json_keys_from_text(input_text):
    json_matches = re.finditer(r'\{(?:[^{}]|(?<=\{)[^{}]*(?=\}))*\}', input_text, re.DOTALL)
    json_matches_list = list(json_matches)
    parsed_json_objects = []
    for i, json_match in enumerate(json_matches_list, start=1):
        try:
            json_match_text = json_match.group().replace('\n', '').replace('\r', '').replace('\t', '')
            parsed_json = json.loads(json_match_text)
            keys_without_prefix = [key.replace("CUSTOM_FIELD_TEXT_", "").replace("CUSTOM_FIELD_DATE_TEXT_", "") for key in parsed_json.keys()]
            parsed_json_objects.extend(keys_without_prefix)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON structure {i}: {e}")
    return parsed_json_objects

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        
        if file:
            input_text = file.read().decode('utf-8')
            parsed_json_objects = extract_json_keys_from_text(input_text)
            valid_decoded_results = [decode_base64(json_object) for json_object in parsed_json_objects if decode_base64(json_object) is not None]
            
            return render_template('result.html', results=valid_decoded_results)
    
    return render_template('index.html', error=None)

if __name__ == '__main__':
    app.run(debug=True)

