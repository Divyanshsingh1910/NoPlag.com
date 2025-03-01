import os
import PyPDF2
import re
import subprocess
from PIL import Image
import pytesseract

def extract_text_from_file(file_path):
    """Extract text from various file formats."""
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        # Text file
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # PDF file
        elif ext == '.pdf':
            return extract_text_from_pdf(file_path)
        
        # Image file
        elif ext in ['.jpg', '.jpeg', '.png']:
            return extract_text_from_image(file_path)
        
        # LaTeX file
        elif ext == '.tex':
            return extract_text_from_latex(file_path)
            
        # Unsupported format
        else:
            return None
    except Exception as e:
        print(f"Error extracting text from {filename}: {str(e)}")
        return None

def extract_text_from_pdf(file_path):
    """Extract text from PDF files."""
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def extract_text_from_image(file_path):
    """Extract text from image files using OCR."""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        return None

def extract_text_from_latex(file_path):
    """Extract text from LaTeX files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        latex_content = f.read()
    
    # Remove LaTeX commands and keep main content
    # This is a simple approach - a more robust solution would use a LaTeX parser
    text = re.sub(r'\\begin\{.*?\}|\\\end\{.*?\}', '', latex_content)
    text = re.sub(r'\\[a-zA-Z]+(\{.*?\})*', '', text)
    text = re.sub(r'\$\$(.*?)\$\$', r'\1', text)
    text = re.sub(r'\$(.*?)\$', r'\1', text)
    
    return text

def extract_code_from_file(file_path):
    """Extract code from programming files."""
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error extracting code from {filename}: {str(e)}")
        return None

def process_question(question_content):
    """
    Process the extracted question to make it suitable for LLM input.
    """
    if not question_content:
        return "No question provided."
    
    # Clean up whitespace
    processed = re.sub(r'\s+', ' ', question_content.strip())
    
    """ adjust limit length need if required by the model
        but shouldn't be thing to worry about since this is gemini-2.0-flash model
    """
    # max_length = 10000  # Adjust based on model token limits
    # if len(processed) > max_length:
    #     processed = processed[:max_length] + "..."
    
    return processed

def process_solution(solution_content, solution_format):
    """
    Process the extracted solution to make it suitable for LLM input.
    """
    if not solution_content:
        return "No solution provided."
    
    # Process based on format type
    if solution_format == 'code':
        # For code, preserve whitespace and indentation
        # Just limit length if needed
        """not needed for gemini models"""
        # max_length = 15000 
        # if len(solution_content) > max_length:
        #     return solution_content[:max_length] + "\n# ... (truncated due to length)"
        return solution_content
    else:
        # For text/documents, clean up whitespace
        processed = re.sub(r'\s+', ' ', solution_content.strip())
        
        """not needed for gemini models"""
        # max_length = 10000  # Adjust based on model token limits
        # if len(processed) > max_length:
        #     processed = processed[:max_length] + "..."
        
        return processed