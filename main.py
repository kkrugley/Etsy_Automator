import os
import time
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv, find_dotenv

console = Console()

def check_env_file():
    """Проверяет и при необходимости создает .env файл."""
    env_file = find_dotenv()
    if not env_file:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write('GEMINI_API_KEY=""\n')
        console.print(Panel("[yellow]Файл .env не найден, создан новый. Пожалуйста, укажите ваш API ключ в меню настроек.[/yellow]", border_style="yellow"))
        time.sleep(2.5) # Даем время прочитать сообщение
    load_dotenv(env_file)
    return True


def main():
    """Главная функция приложения."""
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(
        Panel(
            "[bold green]🚀 Etsy Digital Listing Automator[/bold green]\n\n[dim]Версия 2.0 | Инициализация...[/dim]",
            title="Запуск",
            border_style="green",
            padding=(1, 2)
        )
    )
    # Увеличиваем задержку до 2 секунд
    time.sleep(2.0)
    
    if check_env_file():
        # Импортируем здесь, чтобы избежать циклической зависимости
        from src.cli_handler import run_app
        try:
            run_app()
        except KeyboardInterrupt:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("\n\n[bold magenta]Приложение остановлено пользователем. До свидания![/bold magenta]")
    else:
        console.print("\n[bold red]❌ Критическая ошибка с файлом .env.[/bold red]")


if __name__ == "__main__":
    main()