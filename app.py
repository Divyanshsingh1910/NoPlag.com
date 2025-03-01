from flask import Flask, request, jsonify, send_file, Response
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
import threading
import time

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

# Add this global dictionary to store progress
progress_status = {}

@app.route('/api/progress/<session_id>', methods=['GET'])
def get_progress(session_id):
    return jsonify(progress_status.get(session_id, {'percent': 0, 'message': 'Starting...'}))

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_solution():
    try:
        session_id = str(uuid.uuid4())
        progress_status[session_id] = {'percent': 0, 'message': 'Starting...'}
        
        session_dir = os.path.join(app.config['TEMP_FOLDER'], session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Update progress after processing inputs
        progress_status[session_id] = {
            'percent': 25,
            'message': 'Processing the question and solution...'
        }

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

        # Update progress before analysis
        progress_status[session_id] = {
            'percent': 50,
            'message': 'Analyzing the solution...'
        }
        print("Progress: Question and solution processed")
        
        # Step 1: Generate detailed solution idea
        solution_analysis_prompt = get_solution_analysis_prompt(processed_question, processed_solution)
        
        solution_idea_detailed = ask_lm(solution_analysis_prompt)


        # Update progress before rewriting
        progress_status[session_id] = {
            'percent': 75,
            'message': 'Creating new solution...'
        }
        print("Progress: Detailed solution idea generated")
        
        # Step 2: Generate new solution based on the detailed idea
        rewrite_prompt = get_solution_rewrite_prompt(processed_question, solution_idea_detailed, solution_format)
        
        rewritten_solution = ask_lm(rewrite_prompt)


        # Final progress update
        progress_status[session_id] = {
            'percent': 100,
            'message': 'Almost done! saving the file!'
        }
        print("Progress: Rewritten solution generated")
        
        # Save the rewritten solution to a file
        output_filename = f"noplag_solution{'.txt' if solution_format == 'text' else '.py' if solution_format == 'code' else '.txt'}"
        output_path = os.path.join(session_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rewritten_solution)


        print("Progress: Solution saved to file")
        
        # Create a zip file if needed for multiple files or just send the single file
        if os.path.exists(output_path):
            response = send_file(output_path, as_attachment=True, download_name=output_filename)
            response.headers['X-Session-ID'] = session_id
            return response
        else:
            response = jsonify({'error': 'Failed to generate solution'})
            response.headers['X-Session-ID'] = session_id
            return response, 500
        
    except Exception as e:
        progress_status[session_id] = {
            'percent': 0,
            'message': f'Error: {str(e)}'
        }
        response = jsonify({'error': str(e)})
        response.headers['X-Session-ID'] = session_id
        return response, 500
    finally:
        # Clean up temporary files after 5 minutes
        def cleanup():
            time.sleep(300)  # 5 minutes
            progress_status.pop(session_id, None)
            if 'session_dir' in locals() and os.path.exists(session_dir):
                shutil.rmtree(session_dir)
        
        threading.Thread(target=cleanup).start()

if __name__ == '__main__':
    app.run(debug=True)