# NoPlag.com

A weekend project to generate personalized versions of solutions without plagiarism concerns.

## Overview

NoPlag.com allows users to upload a question and an original solution, then generates a completely new solution that:
- Solves the same problem correctly
- Uses a different approach and style
- Avoids plagiarism detection

## Features

- Support for multiple file formats:
  - Questions: Text, PDF, Images (JPG, PNG)
  - Solutions: Text, PDF, Code files (Python, C++, Java, etc.), LaTeX
- Interactive UI with progress tracking
- Completely rewritten solutions using AI
- Download results in original format

## Technology Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Flask (Python)
- AI: Gemini 2.0 Flash model via OpenAI API
- File Processing: PyPDF2, pytesseract

## Setup and Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/noplag.git
cd noplag
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Install Tesseract OCR for image processing:
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Mac: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

4. Set your OpenAI API key:
```
export OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```
python app.py
```

6. Open your browser and navigate to:
```
http://localhost:5000
```

## How It Works

1. User uploads a question and original solution
2. Backend extracts text/code from uploaded files
3. First API call analyzes the solution and creates a detailed idea
4. Second API call rewrites the solution with a new approach
5. User downloads the personalized solution

## File Structure

```
noplag/
│
├── static/
│   ├── styles.css        # CSS styling
│   └── script.js         # Frontend JavaScript
│
├── app.py                # Flask application and main logic
├── preprocess.py         # File processing utilities
├── prompts.py            # LLM prompt templates