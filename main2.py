from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def show_header():
    console.print(Panel("🎓 [bold cyan]School Management System CLI[/bold cyan]", expand=False))

def show_menu():
    table = Table(title="Main Menu")
    table.add_column("Option", style="green", no_wrap=True)
    table.add_column("Action", style="yellow")

    table.add_row("1", "Add Student")
    table.add_row("2", "View Students")
    table.add_row("3", "Exit")

    console.print(table)

def main():
    show_header()
    show_menu()

if __name__ == "__main__":
    main()
