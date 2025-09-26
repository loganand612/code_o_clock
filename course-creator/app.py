from flask import Flask, request, jsonify
from flask_cors import CORS
from content_ingestion import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_pptx,
    extract_text_from_youtube,
    extract_text_from_website,
)
from text_preprocessing import clean_and_chunk_text
from llm_processor import generate_course_from_text

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_content():
    text = ""
    user_prompt = request.form.get('prompt', '')

    if 'file' in request.files:
        file = request.files['file']
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif file.filename.endswith('.docx'):
            text = extract_text_from_docx(file)
        elif file.filename.endswith('.pptx'):
            text = extract_text_from_pptx(file)
    elif 'url' in request.form:
        url = request.form['url']
        if 'youtube.com' in url or 'youtu.be' in url:
            text = extract_text_from_youtube(url)
        else:
            text = extract_text_from_website(url)
    
    chunks = clean_and_chunk_text(text)
    
    course_json = generate_course_from_text(chunks, user_prompt)
    
    response_data = {
        "extracted_text": text,
        "course": course_json
    }
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)