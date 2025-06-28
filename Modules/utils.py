import json, re
from rich.console import Console

console = Console()

"""Utility function for loading files"""

def loadFromFiles(path, key=None):
            try:
                with open(path, 'r') as file:
                    data = json.load(file)
                    if key:
                        return [item[key] for item in data]
                    return data
            except FileNotFoundError:
                console.print(f"[red]{path} file not found![/red]")
                return []


"""Utility function to validate email addresses"""

def is_valid_email(email):
    emailPattern = r'^[a-z0-9._%+-]{3,}@[a-z0-9.-]+\.[a-z]{2,}$'
    return re.match(emailPattern, email) is not None