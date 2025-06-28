import json, re
from rich.console import Console

# create object instance of console
console = Console()

"""
utility class to handle import of json stored \
data for the program

Contains other utility/helper functions as well
"""
class Utils:
    """
    constructor function
    """
    def __init__(self):
        pass

    """
    load available courses in teh university
    """
    def loadCourses(self):
        path = "./Modules/Misc/courses.json"
        retVal = self.loadFromFile(path)

        # return content of function call
        return retVal

    """
    load states and cities in Nigeria
    """
    def loadStates(self, key=None):
        path = "./Modules/Misc/states-and-cities.json"
        retVal = self.loadFromFile(path)

        if key:
            retVal = [item[key] for item in retVal]

        # return content of function call
        return retVal

    """
    load data from specified file path

    @path: file path for data to be loaded
    """
    def loadFromFile(self, path):
        try:
            with open(path, 'r') as file:
                data = file.read()
                data = json.loads(data)
                return data
        except FileNotFoundError:
            console.print(f"[red]{path} file not found![/red]")
            return []

    """
    Utility function to validate email addresses
    """
    def isValidEmail(self, email):
        emailPattern = r'^[a-z0-9._%+-]{3,}@[a-z0-9.-]+\.[a-z]{2,}$'
        return re.match(emailPattern, email) is not None

# create class instance
Utils = Utils()
