import os
import json
from openai import OpenAI

# Get API key from environment variable
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


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
    prompt = f"{user_prompt}\n\n{MASTER_PROMPT}\n\nHere is the content:\n{full_text}"
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates course content in JSON format."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    # The response from the API is a JSON string, so we parse it
    return json.loads(response.choices[0].message.content)