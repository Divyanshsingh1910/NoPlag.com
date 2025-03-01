document.addEventListener('DOMContentLoaded', function() {
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
    
    document.getElementById('noplag-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const questionText = document.getElementById('question-input').value;
        const solutionText = document.getElementById('solution-input').value;
        const questionFile = document.getElementById('question-file').files[0];
        const solutionFile = document.getElementById('solution-file').files[0];
        
        if ((!questionText && !questionFile) || (!solutionText && !solutionFile)) {
            alert('Please provide both a question and a solution.');
            return;
        }
        
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
            const response = await fetch('http://localhost:5000/api/generate', {
                method: 'POST',
                body: formData
            });
            
            const sessionId = response.headers.get('X-Session-ID');
            if (!sessionId) {
                throw new Error('No session ID received from server');
            }
            
            const pollProgress = async () => {
                const progressResponse = await fetch(`http://localhost:5000/api/progress/${sessionId}`);
                const progressData = await progressResponse.json();
                
                console.log('Progress data:', progressData); // For debugging
                progressBar.style.width = `${progressData.percent}%`;
                progressStatus.textContent = progressData.message;
                
                if (progressData.message.startsWith('Error')) {
                    alert(`Error: ${progressData.message}`);
                    formElement.style.display = 'block';
                    progressContainer.style.display = 'none';
                } else if (progressData.percent < 100) {
                    setTimeout(pollProgress, 100);
                } else {
                    // Fetch the result when progress is 100%
                    const resultResponse = await fetch(`http://localhost:5000/api/result/${sessionId}`);
                    if (resultResponse.ok) {
                        const blob = await resultResponse.blob();
                        const downloadUrl = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = downloadUrl;
                        a.download = solutionFile ? `noplag_solution.${solutionFile.name.split('.').pop()}` : 'noplag_solution.txt';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        
                        setTimeout(() => {
                            formElement.style.display = 'block';
                            progressContainer.style.display = 'none';
                            progressBar.style.width = '0%';
                            document.getElementById('noplag-form').reset();
                        }, 3000);
                    } else {
                        const errorData = await resultResponse.json();
                        alert(`Error: ${errorData.error || 'Failed to get result'}`);
                        formElement.style.display = 'block';
                        progressContainer.style.display = 'none';
                    }
                }
            };
            
            pollProgress();
            
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred in the frontend. Please try again later.');
            formElement.style.display = 'block';
            progressContainer.style.display = 'none';
        }
    });
});