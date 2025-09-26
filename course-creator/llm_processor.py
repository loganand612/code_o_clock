import os
import json
import google.generativeai as genai

# Get API key from environment variable
if not os.environ.get("GOOGLE_API_KEY"):
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")

# Configure the Gemini API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

MASTER_PROMPT = """
You are an expert Course Designer AI.
Your task is to take raw content and create a structured learning course.

### Rules:
1. Always output valid JSON only.
2. Follow this schema exactly:
   {
     "course": "Course Title",
     "modules": [
       {
         "title": "Module Title",
         "lessons": [
           {
             "title": "Lesson Title",
             "summary": "Short overview (2-3 sentences, max 50 words).",
             "detail": "Full explanation (at least 250-400 words). Include definitions, concepts, real-world examples, and applications."
           }
         ]
       }
     ]
   }

### Guidelines:
- Split the content logically into **modules**.
- Group related lessons into the right module.
- Each lesson must have:
  - `summary`: a short, simple description for quick reading.
  - `detail`: a complete explanation in depth (like an article).
- If the input is too long, summarize only the most important lessons.
- Ensure output is always in valid JSON.
"""

def generate_course_from_text(text_chunks, user_prompt):
    # Combine the chunks into a single text for the LLM
    full_text = "\n".join(text_chunks)
    
    # Combine the user's prompt, the master prompt, and the text
    prompt = f"{user_prompt}\n\n{MASTER_PROMPT}\n\nHere is the content:\n{full_text}\n\nRemember to respond with valid JSON only."
    
    # Generate content using Gemini
    response = model.generate_content(prompt)
    
    try:
        # Try to extract JSON from the response
        # First, try to parse the response directly
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the text
            # Look for content between curly braces
            json_text = response.text
            start_idx = json_text.find('{')
            end_idx = json_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_text = json_text[start_idx:end_idx]
                return json.loads(json_text)
            else:
                raise ValueError("Could not extract valid JSON from response")
    except Exception as e:
        # If JSON parsing fails, return an error structure
        return {
            "course": "Error in Course Generation",
            "modules": [{
                "title": "Error",
                "lessons": [{
                    "title": "Error in Processing",
                    "summary": f"Failed to generate course content: {str(e)}",
                    "detail": "There was an error in processing the content. Please try again with different content or check the input format."
                }]
            }]
        }