#!/usr/bin/env python3
"""
Simple script to start the Flask server with proper environment setup
"""
import os
import sys

# Set the Groq API key
os.environ['GROQ_API_KEY'] = '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'

print("Environment variables set:")
print(f"GROQ_API_KEY: {os.environ.get('GROQ_API_KEY', 'NOT SET')}")

try:
    print("Importing Flask app...")
    from app import app
    print("Flask app imported successfully!")
    
    print("Starting Flask server on http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    
    # Start the server
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        use_reloader=False  # Disable reloader to avoid issues
    )
    
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
