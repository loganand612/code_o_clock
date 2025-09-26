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
You are an expert Course Designer AI with deep expertise in educational content creation and curriculum development.
Your task is to transform raw content into a comprehensive, structured learning course that provides real educational value.

### Core Mission:
Create a professional-grade course that feels like a complete educational experience, not just a summary. Each lesson should be substantial, informative, and engaging.

### Rules:
1. Always output valid JSON only - no markdown, no explanations outside JSON.
2. Follow this schema exactly:
   {
     "course": "Course Title",
     "modules": [
       {
         "title": "Module Title",
         "lessons": [
           {
             "title": "Lesson Title",
             "summary": "Concise overview (2-3 sentences, max 50 words) that captures the essence.",
             "detail": "Comprehensive explanation (400-600 words). Must include: clear definitions, key concepts, real-world examples, practical applications, common misconceptions, and actionable insights."
           }
         ]
       }
     ]
   }

### Content Quality Standards:
- **Depth**: Each lesson should be substantial enough to stand alone as educational content
- **Clarity**: Use clear, accessible language while maintaining academic rigor
- **Practicality**: Include real-world examples and applications
- **Structure**: Organize information logically with clear progression
- **Completeness**: Cover topics thoroughly, not just surface-level

### Module Organization Guidelines:
- **Logical Progression**: Modules should build upon each other in a meaningful sequence
- **Balanced Content**: Each module should have 3-6 lessons for optimal learning
- **Clear Themes**: Each module should have a distinct, focused theme
- **Comprehensive Coverage**: Ensure all important aspects of the topic are covered

### Lesson Content Requirements:
- **Introduction**: Start with context and importance
- **Core Concepts**: Explain key ideas with clear definitions
- **Examples**: Provide concrete, relatable examples
- **Applications**: Show how concepts are used in practice
- **Common Pitfalls**: Address typical misconceptions or challenges
- **Takeaways**: End with key insights or actionable points

### Content Adaptation:
- If content is extensive, prioritize the most important and foundational concepts
- If content is limited, expand with related concepts and examples
- Always maintain educational value and depth
- Ensure each lesson provides genuine learning value

### Output Requirements:
- JSON format only
- No additional text or explanations
- Valid JSON structure that can be parsed directly
- All fields must be populated with meaningful content
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

def generate_lesson_content(lesson_title, lesson_summary, context_chunks):
    """
    Generate detailed lesson content using RAG from context chunks
    """
    # Combine context chunks
    context_text = "\n".join(context_chunks) if context_chunks else ""
    
    # Create a focused prompt for lesson content generation
    lesson_prompt = f"""
    You are an expert educator creating detailed lesson content.
    
    Lesson Title: {lesson_title}
    Lesson Summary: {lesson_summary}
    
    Context from source materials:
    {context_text}
    
    Create a comprehensive, detailed lesson that:
    1. Starts with a clear introduction to the topic
    2. Explains key concepts with clear definitions
    3. Provides real-world examples and applications
    4. Addresses common misconceptions or challenges
    5. Includes practical insights and takeaways
    6. Is written in an engaging, educational tone
    7. Is 500-800 words long
    8. Uses the provided context to ensure accuracy and depth
    
    Write the lesson content directly without any formatting or JSON structure.
    """
    
    try:
        response = model.generate_content(lesson_prompt)
        return response.text
    except Exception as e:
        return f"Error generating lesson content: {str(e)}. Please try again."