document.addEventListener('DOMContentLoaded', () => {
    const questionInput = document.getElementById('questionInput');
    const submitButton = document.getElementById('submitButton');
    const buttonText = document.getElementById('buttonText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const answerOutput = document.getElementById('answerOutput');
    const errorMessage = document.getElementById('errorMessage');

    // IMPORTANT: Replace with your FastAPI backend URL when deployed
    // For local development, if FastAPI runs on 8000:
    const API_URL = 'http://localhost:8000/predict';

    submitButton.addEventListener('click', async () => {
        const question = questionInput.value.trim();

        if (!question) {
            alert('Please enter a question.'); // Using alert for simplicity, consider a custom modal in production
            return;
        }

        // Show loading state
        submitButton.disabled = true;
        buttonText.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
        answerOutput.innerHTML = '<p class="placeholder-text">جاري البحث عن الإجابة...</p>';
        errorMessage.classList.add('hidden'); // Hide any previous error message

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.answer) {
                answerOutput.innerHTML = `<p>${data.answer}</p>`;
            } else {
                answerOutput.innerHTML = '<p class="placeholder-text">لم يتم العثور على إجابة واضحة.</p>';
            }

        } catch (error) {
            console.error('Error fetching answer:', error);
            errorMessage.classList.remove('hidden');
            answerOutput.innerHTML = '<p class="placeholder-text">الإجابة ستظهر هنا...</p>'; // Reset answer box
        } finally {
            // Revert loading state
            submitButton.disabled = false;
            buttonText.classList.remove('hidden');
            loadingSpinner.classList.add('hidden');
        }
    });
});