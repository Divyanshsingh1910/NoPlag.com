document.addEventListener('DOMContentLoaded', function() {
    // Show filename when a file is selected
    document.getElementById('question-file').addEventListener('change', function() {
        if (this.files.length > 0) {
            document.getElementById('question-input').value = this.files[0].name;
        }
    });
    
    document.getElementById('solution-file').addEventListener('change', function() {
        if (this.files.length > 0) {
            document.getElementById('solution-input').value = this.files[0].name;
        }
    });
    
    // Form submission handler
    document.getElementById('noplag-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate inputs
        const questionText = document.getElementById('question-input').value;
        const solutionText = document.getElementById('solution-input').value;
        const questionFile = document.getElementById('question-file').files[0];
        const solutionFile = document.getElementById('solution-file').files[0];
        
        if ((!questionText && !questionFile) || (!solutionText && !solutionFile)) {
            alert('Please provide both a question and a solution.');
            return;
        }
        
        // Show progress bar
        const formElement = document.getElementById('noplag-form');
        const progressContainer = document.getElementById('progress-container');
        const progressBar = document.getElementById('progress-bar');
        const progressStatus = document.getElementById('progress-status');
        
        formElement.style.display = 'none';
        progressContainer.style.display = 'block';
        
        const formData = new FormData();
        formData.append('question_text', questionText);
        formData.append('solution_text', solutionText);
        
        if (questionFile) formData.append('question_file', questionFile);
        if (solutionFile) formData.append('solution_file', solutionFile);
        
        try {
            // Simulate progress for better UX
            const progressSteps = [
                { percent: 25, message: 'Step 1/4: Processing input files...' },
                { percent: 50, message: 'Step 2/4: Analyzing solution...' },
                { percent: 75, message: 'Step 3/4: Generating new approach...' },
                { percent: 90, message: 'Step 4/4: Creating personalized solution...' }
            ];
            
            let currentStep = 0;
            
            // Start progress animation
            const progressInterval = setInterval(() => {
                if (currentStep < progressSteps.length) {
                    progressBar.style.width = progressSteps[currentStep].percent + '%';
                    progressStatus.textContent = progressSteps[currentStep].message;
                    currentStep++;
                } else {
                    clearInterval(progressInterval);
                }
            }, 2000); // Update every 2 seconds
            
            // Make API call to the backend
            const response = await fetch('http://localhost:5000/api/generate', {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json, text/plain, */*'
                }
            });

            // Handle response based on content type
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to generate solution');
            }
            
            // Clear the interval once the response is received
            clearInterval(progressInterval);
            
            if (response.ok) {
                // Set progress to 100%
                progressBar.style.width = '100%';
                progressStatus.textContent = 'Done! Downloading your solution...';
                
                const result = await response.blob();
                // Create download link for the generated solution
                const downloadUrl = URL.createObjectURL(result);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = 'noplag_solution' + (solutionFile ? '.' + solutionFile.name.split('.').pop() : '.txt');
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                
                // Reset the form after 3 seconds
                setTimeout(() => {
                    formElement.style.display = 'block';
                    progressContainer.style.display = 'none';
                    progressBar.style.width = '0%';
                    document.getElementById('noplag-form').reset();
                }, 3000);
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.error || 'Failed to generate solution'}`);
                formElement.style.display = 'block';
                progressContainer.style.display = 'none';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred in the frontend. Please try again later.');
            formElement.style.display = 'block';
            progressContainer.style.display = 'none';
        }
    });
});