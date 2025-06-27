document.addEventListener('DOMContentLoaded', () => {
    // --- НАСТРОЙКИ ---
    // Используем имя модели в точности как в твоей документации
    const MODEL_NAME = 'gemini-2.5-flash'; 
    const API_VERSION = 'v1beta'; // Указываем версию API
    // -----------------

    const apiKeyView = document.getElementById('api-key-view');
    const mainAppView = document.getElementById('main-app-view');
    const apiKeyInput = document.getElementById('apiKey');
    const productIdeaInput = document.getElementById('productIdea');
    const statusLine = document.getElementById('status-line');
    
    const resultContainer = document.getElementById('result-container');
    const resultTitle = document.getElementById('result-title-content');
    const resultDescription = document.getElementById('result-description-content');
    const resultTags = document.getElementById('result-tags-content');

    function initialize() {
        const savedApiKey = localStorage.getItem('geminiApiKey');
        if (savedApiKey) {
            showMainApp();
        } else {
            showApiKeyPrompt();
        }
    }

    function showApiKeyPrompt() {
        apiKeyView.style.display = 'block';
        mainAppView.style.display = 'none';
        apiKeyInput.focus();
    }

    function showMainApp() {
        apiKeyView.style.display = 'none';
        mainAppView.style.display = 'block';
        productIdeaInput.focus();
    }
    
    apiKeyInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            const apiKey = apiKeyInput.value.trim();
            if (apiKey) {
                localStorage.setItem('geminiApiKey', apiKey);
                showMainApp();
            }
        }
    });

    productIdeaInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleGeneration();
        }
    });

    async function handleGeneration() {
        const apiKey = localStorage.getItem('geminiApiKey');
        const productIdea = productIdeaInput.value.trim();

        if (!productIdea) {
            setStatus("Ошибка: Поле с описанием товара не может быть пустым.", true);
            return;
        }

        setStatus('<span><div class="loader"></div>Генерация... Пожалуйста, подождите.</span>');
        resultContainer.style.display = 'none';

        try {
            const templateResponse = await fetch('guidelines.txt');
            if (!templateResponse.ok) throw new Error("Не удалось загрузить guidelines.txt");
            const template = await templateResponse.text();
            const prompt = template.replace('{product_idea}', productIdea);
            
            // --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
            // Формируем URL и тело запроса в точности по официальной документации
            const apiUrl = `https://generativelanguage.googleapis.com/${API_VERSION}/models/${MODEL_NAME}:generateContent?key=${apiKey}`;
            
            const requestBody = {
                contents: [{
                    parts: [{
                        text: prompt
                    }]
                }]
            };
            // ------------------------

            const apiResponse = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (!apiResponse.ok) {
                const errorData = await apiResponse.json();
                const errorMessage = errorData?.error?.message || 'Неизвестная ошибка API';
                throw new Error(`API Error: ${errorMessage}`);
            }

            const responseData = await apiResponse.json();
            const rawText = responseData.candidates[0].content.parts[0].text;
            
            const cleanedText = rawText.replace(/```json/g, '').replace(/```/g, '').trim();
            const listingData = JSON.parse(cleanedText);

            setStatus("✅ Генерация успешно завершена!", false, 2000);
            displayResults(listingData);

        } catch (error) {
            setStatus(`❌ Произошла ошибка: ${error.message}`, true);
        }
    }

    function displayResults(data) {
        resultTitle.textContent = data.title || 'N/A';
        resultDescription.textContent = data.description || 'N/A';
        resultTags.textContent = (data.tags || []).join(', ');
        resultContainer.style.display = 'block';
    }

    function setStatus(message, isError = false, clearAfter = 0) {
        statusLine.innerHTML = message;
        statusLine.style.color = isError ? 'var(--error-color)' : 'var(--status-color)';
        if (clearAfter > 0) {
            setTimeout(() => { statusLine.innerHTML = ''; }, clearAfter);
        }
    }

    initialize();
});