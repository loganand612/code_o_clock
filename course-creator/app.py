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
from ai_providers import ai_manager
from chroma_storage import ChromaDocumentStore
from translation_service import translation_service

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
            
            # Generate course using AI manager with fallback
            generated_course = ai_manager.generate_course(chunks, user_prompt)
            
            response_data = {
                "course_id": course_id,
                "extracted_text": text,
                "course": generated_course
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
    try:
        data = request.get_json()
        query = data.get('query', '')
        course_id = data.get('course_id', '')
        n_results = data.get('n_results', 5)
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Search in ChromaDB
        results = document_store.search_content(query, n_results)
        
        return jsonify({
            "results": results,
            "query": query
        })
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

@app.route('/lesson-content', methods=['POST'])
def get_lesson_content():
    """
    Get detailed lesson content using RAG from ChromaDB
    """
    try:
        data = request.get_json()
        lesson_title = data.get('lesson_title', '')
        lesson_summary = data.get('lesson_summary', '')
        course_id = data.get('course_id', '')
        
        if not lesson_title:
            return jsonify({"error": "Lesson title is required"}), 400
        
        # Create a comprehensive query for RAG
        query = f"{lesson_title} {lesson_summary}"
        
        # Search for relevant content
        search_results = document_store.search_content(query, n_results=10)
        
        # Combine the search results into context
        context_chunks = []
        if search_results and 'documents' in search_results:
            for doc_list in search_results['documents']:
                for doc in doc_list:
                    if doc and len(doc.strip()) > 50:  # Filter out very short chunks
                        context_chunks.append(doc)
        
        # Create comprehensive lesson content using the context
        lesson_content = ai_manager.generate_lesson_content(
            lesson_title=lesson_title,
            lesson_summary=lesson_summary,
            context_chunks=context_chunks
        )
        
        return jsonify({
            "lesson_title": lesson_title,
            "content": lesson_content,
            "context_sources": len(context_chunks)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate lesson content: {str(e)}"}), 500
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

@app.route('/translate', methods=['POST'])
def translate_content():
    """
    Translate text content to target language
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'ta')  # Default to Tamil
        source_lang = data.get('source_lang', 'auto')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Translate the text
        translated_text = translation_service.translate_text(text, source_lang, target_lang)
        
        return jsonify({
            "original_text": text,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "target_lang_name": translation_service.get_language_name(target_lang)
        })
        
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

@app.route('/translate-lesson', methods=['POST'])
def translate_lesson():
    """
    Translate lesson content preserving formatting
    """
    try:
        data = request.get_json()
        content = data.get('content', '')
        target_lang = data.get('target_lang', 'ta')  # Default to Tamil
        
        if not content:
            return jsonify({"error": "Content is required"}), 400
        
        # Translate lesson content
        translated_content = translation_service.translate_lesson_content(content, target_lang)
        
        return jsonify({
            "original_content": content,
            "translated_content": translated_content,
            "target_lang": target_lang,
            "target_lang_name": translation_service.get_language_name(target_lang)
        })
        
    except Exception as e:
        return jsonify({"error": f"Lesson translation failed: {str(e)}"}), 500

@app.route('/languages', methods=['GET'])
def get_supported_languages():
    """
    Get list of supported languages for translation
    """
    try:
        languages = translation_service.get_supported_languages()
        return jsonify({
            "languages": languages,
            "default_languages": {
                "en": "English",
                "ta": "Tamil",
                "hi": "Hindi",
                "es": "Spanish",
                "fr": "French",
                "de": "German",
                "zh": "Chinese",
                "ja": "Japanese"
            }
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get languages: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
