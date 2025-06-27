document.addEventListener('DOMContentLoaded', () => {
    // --- Получаем все нужные элементы со страницы ---
    const apiKeyView = document.getElementById('api-key-view');
    const mainAppView = document.getElementById('main-app-view');
    const apiKeyInput = document.getElementById('apiKey');
    const productIdeaInput = document.getElementById('productIdea');
    const statusLine = document.getElementById('status-line');
    
    const resultContainer = document.getElementById('result-container');
    const resultTitle = document.getElementById('result-title-content');
    const resultDescription = document.getElementById('result-description-content');
    const resultTags = document.getElementById('result-tags-content');

    // --- Главная логика при загрузке страницы ---
    function initialize() {
        const savedApiKey = localStorage.getItem('geminiApiKey');
        if (savedApiKey) {
            showMainApp();
        } else {
            showApiKeyPrompt();
        }
    }

    // --- Функции для переключения "экранов" ---
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
    
    // --- Обработчики событий ---

    // 1. Ввод API ключа и нажатие Enter
    apiKeyInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            const apiKey = apiKeyInput.value.trim();
            if (apiKey) {
                localStorage.setItem('geminiApiKey', apiKey);
                console.log('API Key saved.');
                showMainApp();
            }
        }
    });

    // 2. Ввод идеи товара и нажатие Enter
    productIdeaInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleGeneration();
        }
    });

    // --- Основная функция генерации ---
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
            // Загружаем шаблон промпта
            const templateResponse = await fetch('guidelines.txt');
            if (!templateResponse.ok) throw new Error("Не удалось загрузить guidelines.txt");
            const template = await templateResponse.text();

            // Формируем промпт
            const prompt = template.replace('{product_idea}', productIdea);
            
            // Отправляем запрос к Gemini API
            const apiResponse = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
            });

            if (!apiResponse.ok) {
                const errorData = await apiResponse.json();
                throw new Error(`API Error: ${errorData.error.message}`);
            }

            const responseData = await apiResponse.json();
            const rawText = responseData.candidates[0].content.parts[0].text;
            
            // Парсим JSON и отображаем результат
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
            setTimeout(() => {
                statusLine.innerHTML = '';
            }, clearAfter);
        }
    }

    // --- Запускаем приложение ---
    initialize();
});