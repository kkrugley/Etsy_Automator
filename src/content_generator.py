import os
import json
import google.generativeai as genai
from rich.console import Console
from typing import Optional, Dict

console = Console()

def get_prompt_template() -> Optional[str]:
    filepath = "guidelines.txt"
    try:
        if not os.path.exists(filepath):
            console.print(f"[bold red]Ошибка: Файл {filepath} не найден.[/bold red]")
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            template = f.read()
        if not template:
            console.print(f"[bold red]Ошибка: Файл {filepath} пуст.[/bold red]")
            return None
        return template
    except Exception as e:
        console.print(f"[bold red]Ошибка при чтении файла {filepath}: {e}.[/bold red]")
        return None

def generate_listing_content(product_idea: str) -> Optional[Dict]:
    """
    Принимает идею, формирует промпт и генерирует контент с помощью AI.
    """
    console.print("\n[bold]Генерация контента с помощью AI...[/bold]")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print("[bold red]Ошибка: GEMINI_API_KEY не найден.[/bold red]")
        return None

    template = get_prompt_template()
    if not template: return None

    prompt = template.format(product_idea=product_idea)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        model.safety_settings = { # type: ignore
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE', 'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE', 'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
        }
        with console.status("[bold green]Отправляю запрос к Gemini API...", spinner="earth"):
            response = model.generate_content(prompt)
        
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        generated_data = json.loads(cleaned_response_text, strict=False)
        
        console.print("✅ [green]Контент успешно сгенерирован![/green]")
        return generated_data
    except Exception as e:
        console.print(f"[bold red]Ошибка при генерации контента: {e}[/bold red]")
        response_text = "No API response received."
        if 'response' in locals() and hasattr(response, 'text'):
            response_text = response.text
        console.print(f"[dim]Текст ответа от API: {response_text}[/dim]")
        return None