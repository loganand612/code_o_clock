from flask import Flask, request, jsonify, send_file
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
from video_generator import video_generator
import os
import uuid

app = Flask(__name__)
CORS(app)

# Initialize ChromaDB
document_store = ChromaDocumentStore()

@app.route('/upload', methods=['POST'])
def upload_content():
    try:
        all_text_content = []
        user_prompt = request.form.get('prompt', '')
        source_info = {
            "sources": [],
            "prompt": user_prompt
        }
        
        # Check if we have any content sources
        has_files = 'file' in request.files and request.files['file'].filename
        has_urls = request.form.get('urls') or request.form.get('url')
        
        if not has_files and not has_urls:
            return jsonify({"error": "No file or URL provided"}), 400

        # Process files
        if has_files:
            files = request.files.getlist('file')  # Support multiple files
            for file in files:
                if file.filename:
                    file_source_info = {
                        "type": file.filename.split('.')[-1].lower(),
                        "name": file.filename,
                        "source_type": "file"
                    }
                    
                    try:
                        if file.filename.endswith('.pdf'):
                            text = extract_text_from_pdf(file)
                        elif file.filename.endswith('.docx'):
                            text = extract_text_from_docx(file)
                        elif file.filename.endswith('.pptx'):
                            text = extract_text_from_pptx(file)
                        else:
                            continue  # Skip unsupported files
                            
                        if text.strip():
                            all_text_content.append({
                                "content": text,
                                "source": file_source_info
                            })
                            source_info["sources"].append(file_source_info)
                    except Exception as e:
                        app.logger.warning(f"Failed to extract content from {file.filename}: {str(e)}")
                        continue

        # Process URLs
        urls_to_process = []
        if request.form.get('urls'):
            # Multiple URLs (comma-separated or JSON array)
            urls_text = request.form.get('urls')
            try:
                import json
                urls_to_process = json.loads(urls_text)
            except:
                # If not JSON, treat as comma-separated
                urls_to_process = [url.strip() for url in urls_text.split(',') if url.strip()]
        elif request.form.get('url'):
            # Single URL
            urls_to_process = [request.form.get('url')]
            
        for url in urls_to_process:
            if url:
                url_source_info = {
                    "type": "youtube" if ('youtube.com' in url or 'youtu.be' in url) else "website",
                    "name": url,
                    "source_type": "url"
                }
                
                try:
                    if 'youtube.com' in url or 'youtu.be' in url:
                        text = extract_text_from_youtube(url)
                    else:
                        text = extract_text_from_website(url)
                        
                    if text.strip():
                        all_text_content.append({
                            "content": text,
                            "source": url_source_info
                        })
                        source_info["sources"].append(url_source_info)
                except Exception as e:
                    app.logger.warning(f"Failed to extract content from {url}: {str(e)}")
                    continue

        if not all_text_content:
            return jsonify({"error": "No content could be extracted from any source"}), 400

        # Combine all extracted content
        combined_text = ""
        for i, content_item in enumerate(all_text_content):
            source_info_text = f"\n\n--- Content from {content_item['source']['name']} ({content_item['source']['type']}) ---\n\n"
            combined_text += source_info_text + content_item['content']
            
        # Clean and chunk the combined text
        try:
            chunks = clean_and_chunk_text(combined_text)
            if not chunks:
                return jsonify({"error": "Content processing failed"}), 400
        except Exception as e:
            return jsonify({"error": f"Failed to process text: {str(e)}"}), 500

        try:
            # Store chunks in ChromaDB
            course_id = document_store.store_course_content(chunks, source_info)
            
            # Generate course using LLM with enhanced prompt processing
            if user_prompt.strip():
                # Use the LLM to generate structured course content
                generated_course = generate_course_from_text(chunks, user_prompt)
            else:
                # Generate a basic course structure from the content
                generated_course = generate_course_from_text(chunks, "Create a comprehensive course from this content")
            
            response_data = {
                "course_id": course_id,
                "extracted_text": combined_text,
                "course": generated_course,
                "sources_processed": len(source_info["sources"]),
                "source_info": source_info
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

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """Generate a summary video with enhanced features"""
    data = request.json
    title = data.get('title', 'Course Summary')
    summary = data.get('summary', '')
    style = data.get('style', 'modern')  # modern, minimal, educational
    duration = data.get('duration', 60)  # Duration in seconds
    
    if not summary:
        return jsonify({'error': 'No summary provided'}), 400

    try:
        # Generate video using the enhanced video generator
        video_path = video_generator.create_summary_video(
            title=title,
            summary=summary,
            style=style,
            duration=duration
        )
        
        if not video_path or not os.path.exists(video_path):
            return jsonify({'error': 'Failed to generate video'}), 500
        
        # Generate unique filename for download
        video_filename = f"summary_{uuid.uuid4()[:8]}.mp4"
        final_path = os.path.join('generated_videos', video_filename)
        
        # Create directory if it doesn't exist
        os.makedirs('generated_videos', exist_ok=True)
        
        # Move video to final location
        import shutil
        shutil.move(video_path, final_path)
        
        return jsonify({
            'video_url': f'/download-video/{video_filename}',
            'video_id': video_filename,
            'style': style,
            'duration': duration,
            'title': title
        })
        
    except Exception as e:
        app.logger.error(f"Video generation error: {str(e)}")
        return jsonify({'error': f'Video generation failed: {str(e)}'}), 500

@app.route('/generate-lesson-video', methods=['POST'])
def generate_lesson_video():
    """Generate a video for a specific lesson"""
    data = request.json
    lesson_title = data.get('lesson_title', 'Lesson')
    lesson_summary = data.get('lesson_summary', '')
    lesson_detail = data.get('lesson_detail', '')
    style = data.get('style', 'educational')
    
    if not lesson_summary and not lesson_detail:
        return jsonify({'error': 'No lesson content provided'}), 400

    try:
        # Combine summary and detail for video content
        video_content = f"{lesson_summary}\n\n{lesson_detail[:300]}..." if len(lesson_detail) > 300 else f"{lesson_summary}\n\n{lesson_detail}"
        
        # Generate video
        video_path = video_generator.create_summary_video(
            title=lesson_title,
            summary=video_content,
            style=style,
            duration=90  # Slightly longer for lessons
        )
        
        if not video_path or not os.path.exists(video_path):
            return jsonify({'error': 'Failed to generate lesson video'}), 500
        
        # Generate unique filename
        video_filename = f"lesson_{uuid.uuid4()[:8]}.mp4"
        final_path = os.path.join('generated_videos', video_filename)
        
        # Create directory if it doesn't exist
        os.makedirs('generated_videos', exist_ok=True)
        
        # Move video to final location
        import shutil
        shutil.move(video_path, final_path)
        
        return jsonify({
            'video_url': f'/download-video/{video_filename}',
            'video_id': video_filename,
            'lesson_title': lesson_title,
            'style': style,
            'duration': 90
        })
        
    except Exception as e:
        app.logger.error(f"Lesson video generation error: {str(e)}")
        return jsonify({'error': f'Lesson video generation failed: {str(e)}'}), 500

@app.route('/generate-course-overview', methods=['POST'])
def generate_course_overview():
    """Generate an overview video for the entire course"""
    data = request.json
    course_title = data.get('course_title', 'Course Overview')
    course_description = data.get('course_description', '')
    modules = data.get('modules', [])
    
    if not course_description and not modules:
        return jsonify({'error': 'No course content provided'}), 400

    try:
        # Create overview content
        overview_content = f"Welcome to {course_title}!\n\n{course_description}\n\n"
        
        if modules:
            overview_content += "This course includes the following modules:\n"
            for i, module in enumerate(modules[:5], 1):  # Limit to 5 modules
                overview_content += f"{i}. {module.get('title', 'Module')}\n"
        
        # Generate video
        video_path = video_generator.create_summary_video(
            title=f"{course_title} - Overview",
            summary=overview_content,
            style='modern',
            duration=120  # 2 minutes for overview
        )
        
        if not video_path or not os.path.exists(video_path):
            return jsonify({'error': 'Failed to generate course overview video'}), 500
        
        # Generate unique filename
        video_filename = f"overview_{uuid.uuid4()[:8]}.mp4"
        final_path = os.path.join('generated_videos', video_filename)
        
        # Create directory if it doesn't exist
        os.makedirs('generated_videos', exist_ok=True)
        
        # Move video to final location
        import shutil
        shutil.move(video_path, final_path)
        
        return jsonify({
            'video_url': f'/download-video/{video_filename}',
            'video_id': video_filename,
            'course_title': course_title,
            'style': 'modern',
            'duration': 120
        })
        
    except Exception as e:
        app.logger.error(f"Course overview generation error: {str(e)}")
        return jsonify({'error': f'Course overview generation failed: {str(e)}'}), 500

@app.route('/download-video/<filename>', methods=['GET'])
def download_video(filename):
    """Download generated video file"""
    try:
        video_path = os.path.join('generated_videos', filename)
        if os.path.exists(video_path):
            return send_file(video_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'Video file not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
