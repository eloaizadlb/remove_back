from flask import Flask, request, jsonify
from process_image import remove_background

app = Flask(__name__)

@app.route('/remove_background', methods=['POST'])
def remove_background_endpoint():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        image_base64 = data['image']
        output_base64 = remove_background(image_base64)
        return jsonify({'output': output_base64}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
