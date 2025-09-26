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
from chroma_storage import ChromaDocumentStore

app = Flask(__name__)
CORS(app)

# Initialize ChromaDB
document_store = ChromaDocumentStore()

@app.route('/upload', methods=['POST'])
def upload_content():
    try:
        text = ""
        user_prompt = request.form.get('prompt', '')
        source_info = {}
        
        if not request.files and not request.form.get('url'):
            return jsonify({"error": "No file or URL provided"}), 400

        if 'file' in request.files:
            file = request.files['file']
            if not file.filename:
                return jsonify({"error": "No file selected"}), 400
                
            source_info = {
                "type": file.filename.split('.')[-1].lower(),
                "name": file.filename
            }
            
            try:
                if file.filename.endswith('.pdf'):
                    text = extract_text_from_pdf(file)
                elif file.filename.endswith('.docx'):
                    text = extract_text_from_docx(file)
                elif file.filename.endswith('.pptx'):
                    text = extract_text_from_pptx(file)
                else:
                    return jsonify({"error": "Unsupported file type"}), 400
            except Exception as e:
                return jsonify({"error": f"Failed to extract content: {str(e)}"}), 500
                
        elif 'url' in request.form:
            url = request.form['url']
            if not url:
                return jsonify({"error": "No URL provided"}), 400
                
            source_info = {
                "type": "youtube" if ('youtube.com' in url or 'youtu.be' in url) else "website",
                "name": url
            }
            
            try:
                if 'youtube.com' in url or 'youtu.be' in url:
                    text = extract_text_from_youtube(url)
                else:
                    text = extract_text_from_website(url)
            except Exception as e:
                return jsonify({"error": f"Failed to extract content: {str(e)}"}), 500

        if not text.strip():
            return jsonify({"error": "No content could be extracted"}), 400

        # Clean and chunk the text
        try:
            chunks = clean_and_chunk_text(text)
            if not chunks:
                return jsonify({"error": "Content processing failed"}), 400
        except Exception as e:
            return jsonify({"error": f"Failed to process text: {str(e)}"}), 500

        try:
            # Store chunks in ChromaDB
            course_id = document_store.store_course_content(chunks, source_info)
            
            # For testing: Skip LLM generation and return dummy course structure
            dummy_course = {
                "course": "Test Course",
                "modules": [{
                    "title": "Test Module",
                    "lessons": [{
                        "title": "Test Lesson",
                        "summary": "Test summary of extracted content",
                        "detail": text[:500] if len(text) > 500 else text  # First 500 chars of extracted text
                    }]
                }]
            }
            
            response_data = {
                "course_id": course_id,
                "extracted_text": text,
                "course": dummy_course
            }
            return jsonify(response_data)
        except Exception as e:
            return jsonify({"error": f"Failed to store or process content: {str(e)}"}), 500
            
    except Exception as e:
        app.logger.error(f"Upload error: {str(e)}")
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/search', methods=['POST'])
def search_content():
    """
    Search for relevant content in stored courses
    """
    query = request.json.get('query')
    n_results = request.json.get('n_results', 5)
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
        
    results = document_store.search_content(query, n_results)
    return jsonify(results)

@app.route('/course/<course_id>', methods=['GET'])
def get_course(course_id):
    """
    Retrieve all content for a specific course
    """
    try:
        course_content = document_store.get_course_chunks(course_id)
        return jsonify(course_content)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/course/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    """
    Delete a course and all its content
    """
    try:
        document_store.delete_course(course_id)
        return jsonify({"message": "Course deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/all-content', methods=['GET'])
def get_all_content():
    """Get all stored content from ChromaDB"""
    try:
        all_content = document_store.get_all_content()
        return jsonify(all_content)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve content: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
