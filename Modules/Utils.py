import json, re, hashlib
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
            return []

    """
    Utility function to validate email addresses
    """
    def isValidEmail(self, email):
        emailPattern = r'^[a-z0-9._%+-]{3,}@[a-z0-9.-]+\.[a-z]{2,}$'
        return re.match(emailPattern, email) is not None

    """
    ensure a user hasn't applied with given email
    """
    def ensureUniqueEmail(self, email):
        
        dataBase = self.loadFromFile("./Modules/Storage/db.json")

        if not dataBase:
            return
        
        dbIds = dataBase.get("admissionApplications")
        dbEmails = []

        # return if no key found
        if not dbIds:
            return

        for key, value in dbIds.items():
            if "email" in value:
                dbEmails.append(value["email"])
            
        while email in dbEmails:
            console.print(f"[red]\b{email} already exists[/red]")
            email = input("Enter your email address: ").strip()

    """
    view programmes on offer by the school
    """
    def viewProgrammes(self):
        programInfo = Utils.loadCourses()
        schools = programInfo.keys()

        print("\nHere's a list of available programmes:")
        console.print(f"\n[purple]SCHOOLS:\t\t"\
                      "DEPARTMENTS:[/purple]")

        for x in schools:
            # get school dict
            school = programInfo.get(x)

            # print school/faculty name
            console.print(f"\n[green]{x}[/green]")

            for y in school:
                # get department dict
                dept = school.get(y)

                # get department and course code for printing
                deptName = dept.get('course')
                courseCode = dept.get('course code')

                # print departments in the school
                print(f"\t\t\t({courseCode}) - {deptName}")

    """
    create root admin
    """
    def rootAdmin(self):
        password = 'root1234'
        password = hashlib.md5(password.encode())
        password = password.hexdigest()

        admins = {}

        root = {
            'root': {
                'username': 'root',
                'password': password,
                'email': 'root@fut.com',
                'firstName': 'root',
                'lastName': 'root',
                'middleName': None
            }
        }

        admins.update(root)
        return admins

    """
    log the current user out of the portal
    """
    def logout(self, handle):
        if not handle.loggedIn:
            console.print("\n[red]ERROR[/red]\nYou need"\
                          " to be logged in to log out!\n")
        else:
            handle.user = None
            handle.loggedIn = None
            handle.loggedInUser = None
            handle.prompt = handle.defaultPrompt


    """
    purge given string of excess whitespace
    """
    def cleanString(self, string):
        string = string.split()
        string = " ".join(string)

        return string

# create class instance
Utils = Utils()
