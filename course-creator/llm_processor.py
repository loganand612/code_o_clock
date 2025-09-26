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

# LLM processor is disabled. This module now only passes through the summary for video generation.

def generate_course_from_text(text_chunks, user_prompt):
    # Instead of LLM, just return a simple course structure using the extracted text
    summary = text_chunks[0][:200] if text_chunks else "No content available."
    return {
        "course": "Generated Course (No LLM)",
        "modules": [
            {
                "title": "Module 1",
                "lessons": [
                    {
                        "title": "Lesson 1",
                        "summary": summary,
                        "detail": "\n".join(text_chunks) if text_chunks else "No details available."
                    }
                ]
            }
        ]
    }