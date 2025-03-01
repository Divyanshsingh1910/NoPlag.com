from flask import Flask, request, jsonify, send_file
import os
import uuid
import zipfile
import tempfile
import shutil
import traceback
from werkzeug.utils import secure_filename
from openai import OpenAI
from preprocess import (
    extract_text_from_file,
    extract_code_from_file,
    process_question,
    process_solution
)
from prompts import (
    get_solution_analysis_prompt,
    get_solution_rewrite_prompt
)
from flask_cors import CORS  # Add this import

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB max upload size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMP_FOLDER'] = 'temp'

# Make sure upload and temp directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
def ask_lm(prompt):
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_solution():
    try:
        # Create a unique session ID for this request
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(app.config['TEMP_FOLDER'], session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Extract question
        question_text = request.form.get('question_text', '')
        question_content = question_text
        
        if 'question_file' in request.files:
            question_file = request.files['question_file']
            if question_file and question_file.filename:
                filename = secure_filename(question_file.filename)
                file_path = os.path.join(session_dir, filename)
                question_file.save(file_path)
                
                # Extract text from the file
                extracted_question = extract_text_from_file(file_path)
                if extracted_question:
                    question_content = extracted_question
        
        # Process question
        processed_question = process_question(question_content)
        
        # Extract solution
        solution_text = request.form.get('solution_text', '')
        solution_content = solution_text
        solution_format = 'text'
        
        if 'solution_file' in request.files:
            solution_file = request.files['solution_file']
            if solution_file and solution_file.filename:
                filename = secure_filename(solution_file.filename)
                file_path = os.path.join(session_dir, filename)
                solution_file.save(file_path)
                
                # Determine if it's code or document
                ext = os.path.splitext(filename)[1].lower()
                
                if ext in ['.py', '.cpp', '.c', '.java', '.js']:
                    # Extract code
                    extracted_solution = extract_code_from_file(file_path)
                    solution_format = 'code'
                    solution_extension = ext
                else:
                    # Extract text
                    extracted_solution = extract_text_from_file(file_path)
                    solution_format = 'document'
                    solution_extension = ext
                
                if extracted_solution:
                    solution_content = extracted_solution
        
        # Process solution
        processed_solution = process_solution(solution_content, solution_format)
        
        # Step 1: Generate detailed solution idea
        solution_analysis_prompt = get_solution_analysis_prompt(processed_question, processed_solution)
        
        solution_idea_detailed = ask_lm(solution_analysis_prompt)

        print("Progress: Detailed solution idea generated")
        
        # Step 2: Generate new solution based on the detailed idea
        rewrite_prompt = get_solution_rewrite_prompt(processed_question, solution_idea_detailed, solution_format)
        
        rewritten_solution = ask_lm(rewrite_prompt)

        print("Progress: Rewritten solution generated")
        
        # Save the rewritten solution to a file
        output_filename = f"noplag_solution{'.txt' if solution_format == 'text' else '.py' if solution_format == 'code' else '.txt'}"
        output_path = os.path.join(session_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rewritten_solution)

        print("Progress: Solution saved to file")
        
        # Create a zip file if needed for multiple files or just send the single file
        if os.path.exists(output_path):
            # Return the file for download
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        else:
            return jsonify({'error': 'Failed to generate solution'}), 500
        
    except Exception as e:
        print("Error:", str(e))
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temporary files
        try:
            if 'session_dir' in locals() and os.path.exists(session_dir):
                shutil.rmtree(session_dir)
        except Exception as cleanup_error:
            print("Cleanup error:", str(cleanup_error))

if __name__ == '__main__':
    app.run(debug=True)