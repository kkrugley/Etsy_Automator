import re
from rich.console import Console
from typing import Dict, List

console = Console()

STOP_WORDS = set("и в во не что он на я с со как а то все она так его но да ты к у же вы за бы по только еще a an the and is are in on for with that it i you he she they we".split())

def detect_language(text: str) -> str:
    """Определяет язык текста (en или ru) по наличию кириллицы."""
    return 'ru-RU' if re.search('[\u0400-\u04FF]', text) else 'en-US'

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Извлекает ключевые слова из текста, удаляя стоп-слова."""
    words = [word.strip(",.!?") for word in text.lower().split()]
    keywords = [word for word in words if word not in STOP_WORDS]
    return [kw for kw in keywords if kw][:max_keywords]

def analyze_idea(product_idea: str) -> Dict:
    """
    Просто извлекает ключевые слова и определяет язык.
    """
    console.print("\n[bold]Этап 1: Извлечение ключевых слов[/bold]")
    
    keywords = extract_keywords(product_idea)
    if not keywords:
        console.print("[bold red]Не удалось извлечь ключевые слова.[/bold red]")
        return {}
        
    lang = detect_language(product_idea)

    analysis_results = {
        'base_keywords': keywords,
        'language': lang
    }
    
    console.print(f"✅ [green]Ключевые слова извлечены:[/green] {', '.join(keywords)}")
    return analysis_results