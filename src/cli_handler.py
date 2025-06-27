import sys
import os
import json
import re
import time
import subprocess
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from dotenv import set_key, get_key

# Импортируем только генератор
from src.content_generator import generate_listing_content

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def edit_file_in_notepad(filepath: str):
    try:
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f: pass
        subprocess.run(["notepad.exe", filepath], check=True)
        console.print(f"[green]Файл {filepath} был открыт для редактирования.[/green]")
    except Exception as e:
        console.print(f"[red]Не удалось открыть файл в Блокноте: {e}[/red]")

def update_api_key():
    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, 'w', encoding='utf-8') as f: f.write('GEMINI_API_KEY=""\n')
    current_key = get_key(env_file, "GEMINI_API_KEY") or "не задан"
    console.print(f"Текущий API ключ: [cyan]{current_key}[/cyan]")
    new_key = Prompt.ask("[bold]Введите новый GEMINI_API_KEY (оставьте пустым для отмены)[/bold]")
    if new_key.strip():
        set_key(env_file, "GEMINI_API_KEY", new_key)
        console.print("[bold green]✅ API ключ успешно обновлен![/bold green]")
    else:
        console.print("[yellow]Обновление отменено.[/yellow]")
    time.sleep(1.5)

def settings_menu():
    while True:
        clear_screen()
        console.print(Panel(
            "[bold]1.[/bold] Изменить API ключ Gemini\n"
            "[bold]2.[/bold] Редактировать шаблон промпта (guidelines.txt)\n"
            "[bold]3.[/bold] Вернуться в главное меню",
            title="[yellow]⚙️ Меню настроек[/yellow]",
            border_style="yellow"
        ))
        choice = Prompt.ask("[bold]Выберите опцию[/bold]", choices=["1", "2", "3"], default="3")
        if choice == '1': clear_screen(); update_api_key()
        elif choice == '2': edit_file_in_notepad("guidelines.txt")
        elif choice == '3': break

def create_new_listing():
    clear_screen()
    console.print(Panel("Опишите ваш цифровой товар. Чем подробнее, тем лучше.", title="[bold cyan]Идея товара[/bold cyan]"))
    product_idea = Prompt.ask("[bold]✏️ Ваше описание[/bold]")
    if not product_idea.strip():
        console.print("[bold red]Описание не может быть пустым.[/bold red]\n"); return

    clear_screen()
    listing_data = generate_listing_content(product_idea)
    if not listing_data:
        console.print("[bold red]Нажмите Enter для возврата в меню.[/bold red]"); Prompt.ask(); return

    display_generated_content(listing_data)
    save = Prompt.ask("\n[bold]Сохранить этот листинг в JSON-файл?[/bold]", choices=["y", "n"], default="y")
    if save == 'y':
        save_listing_to_file(product_idea, listing_data)
    Prompt.ask("\n[bold]Нажмите Enter, чтобы вернуться в главное меню...[/bold]")

def display_generated_content(listing_data: dict):
    clear_screen()
    console.print(Panel("[bold]Предпросмотр сгенерированного листинга[/bold]", style="bold blue", expand=False))
    main_table = Table(show_header=False, box=None, padding=(0, 1)); main_table.add_column(style="bold cyan"); main_table.add_column()
    main_table.add_row("Заголовок:", listing_data.get('title', 'N/A'))
    main_table.add_row("Описание:", listing_data.get('description', 'N/A').replace('\n\n', '\n'))
    console.print(main_table)
    tags_panel = Panel(', '.join(listing_data.get('tags', [])), title="[bold cyan]Теги (13 шт.)[/bold cyan]", border_style="cyan")
    console.print(tags_panel)

def save_listing_to_file(product_idea: str, listing_data: dict):
    if not os.path.exists('listings'): os.makedirs('listings')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_slug = re.sub(r'[^\w\s-]', '', listing_data.get('title', 'untitled').lower()).strip()
    file_slug = re.sub(r'[\s_-]+', '-', file_slug)[:50]
    filename = f"listings/{timestamp}_{file_slug}.json"
    full_data = {
        "product_idea": product_idea,
        "generated_at_utc": datetime.utcnow().isoformat(),
        "listing_data": listing_data
    }
    try:
        with open(filename, 'w', encoding='utf-8') as f: json.dump(full_data, f, ensure_ascii=False, indent=4)
        console.print(Panel(f"[bold green]✅ Листинг успешно сохранен![/bold green]\n[cyan]Путь к файлу:[/cyan] {filename}", title="Сохранение", border_style="green"))
    except Exception as e: console.print(f"[bold red]Ошибка при сохранении файла: {e}[/bold red]")

def view_saved_listings():
    clear_screen()
    console.print("\n[bold blue]Просмотр сохраненных листингов...[/bold blue]")
    try:
        if not os.path.exists('listings'): os.makedirs('listings')
        files = [f for f in os.listdir('listings') if f.endswith('.json')]
        if not files:
            console.print("[yellow]Папка /listings пуста.[/yellow]\n")
        else:
            files.sort(reverse=True)
            for i, filename in enumerate(files): console.print(f"[bold]{i + 1}.[/bold] {filename}")
            choice = Prompt.ask("\n[bold]Введите номер файла для просмотра (или 'q' для выхода)[/bold]")
            if choice.lower() != 'q':
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(files):
                    filepath = os.path.join('listings', files[selected_index])
                    with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)
                    clear_screen(); console.print_json(data=data)
                else:
                    console.print("[red]Неверный номер файла.[/red]")
    except (ValueError, IndexError):
        console.print("[red]Неверный ввод.[/red]")
    except Exception as e: console.print(f"[red]Ошибка: {e}[/red]")
    Prompt.ask("\n[bold]Нажмите Enter, чтобы вернуться в главное меню...[/bold]")

def run_app():
    while True:
        clear_screen()
        console.print(Panel(
            "[bold]1.[/bold] Создать новый листинг\n"
            "[bold]2.[/bold] Просмотреть сохраненные листинги\n"
            "[bold]3.[/bold] Настройки\n"
            "[bold]4.[/bold] Выход",
            title="[cyan]Главное меню[/cyan]"
        ))
        choice = Prompt.ask("[bold]Выберите опцию[/bold]", choices=["1", "2", "3", "4"], default="1")
        
        if choice == '1': create_new_listing()
        elif choice == '2': view_saved_listings()
        elif choice == '3': settings_menu()
        elif choice == '4':
            clear_screen(); console.print("\n[bold magenta]До встречи![/bold magenta]"); sys.exit()