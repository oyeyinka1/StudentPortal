import json, re, hashlib, string, os
from rich.console import Console
from rich.table import Table

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
        self.paths = {
            "db": "./Modules/Storage/db.json",
            "courses": "./Modules/Storage/courses.json",
            "faculties": "./Modules/Storage/faculties.json",
            "admin_logs": "./Modules/Storage/admin_logs.txt",
            "programmes": "./Modules/Storage/programmes.json",
            "tests_and_exams": "./Modules/Storage/tests_and_exams.json",
            "states_and_cities": "./Modules/Misc/states_and_cities.json"
        }

    """
    load available programmes in the university
    """
    def loadProgrammes(self):
        path = self.paths.get('programmes')
        retVal = self.loadFromFile(path)

        # return content of function call
        return retVal

    """
    load courses for given department and level
    """
    def loadCourses(self, studentInfo=None):
        path = self.paths.get('courses')
        retVal = self.loadFromFile(path)

        if studentInfo:
            school = studentInfo.get('school')
            level = str(studentInfo.get('level'))
            department = studentInfo.get('courseCode').lower()

            retVal = retVal.get(school).get(department).get(level)

        # return courses for current student
        return retVal
        
        
    """
    load states and cities in Nigeria
    """
    def loadStates(self, key=None):
        path = self.paths.get('states_and_cities')
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
        
        dataBase = self.loadFromFile(self.paths.get('db'))

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
        programInfo = self.loadProgrammes()

        # check if file is programme was loaded
        if not programInfo:
            console.print("[yellow]There are no programmes yet![/yellow]")
            return

        schools = programInfo.keys()

        print("\nHere's a list of available programmes:")
        console.print(f"\n[purple]SCHOOLS:\t\t"\
                      "DEPARTMENTS:[/purple]")

        for x in schools:
            # get school dict
            school = programInfo.get(x)

            # print school/faculty name
            console.print(f"\n[green]{x.upper()}[/green]")

            for y in school:
                # get department dict
                dept = school.get(y)

                # get department and course code for printing
                deptName = dept.get('course')
                courseCode = dept.get('course code')

                # print departments in the school
                print(f"\t\t\t({courseCode.upper()}) - {deptName.title()}")

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

    """
    validate given name
    """
    def validateName(self, name):
        alphanumeric = "-'"
        letters = string.ascii_letters

        # valid characters
        acceptedCharacters = f"{letters}{alphanumeric}"

        # check for whitespace in naem
        name = self.cleanString(name)
        if " " in name:
            return "Name cannot contain whitespace!"

        # check for minimum length
        if len(name) < 3:
            return "Minimum name length is 3!"

        # check for maximum length
        if len(name) > 30:
            return "Maximum name length is 30!"

        # check characters in name
        for character in name:
            if character not in acceptedCharacters:
                return "Invalid character in name!"

        # return False if no issue was found with name
        return False

    """
    validate username
    """
    def validateUsername(self, username):
        username = self.cleanString(username)

        alphanumeric = "-_."
        letters = string.ascii_letters

        # valid characters
        acceptedCharacters = f"{letters}{alphanumeric}"

        # check for whitespace
        if " " in username:
            return "username cannot contain whitespace"

        # check accepted characters
        for character in username:
            if character not in acceptedCharacters:
                return f"Invalid character `{character}` in username!"

        # return false if no issue was found with username
        return False

    """
    validate password
    """
    def validatePassword(self, password):
        password = password.strip()

        # check minimum length
        if len(password) < 6:
            return "Password must be at least 6 characters long"

        # return false if no issues found with password
        return False

    """
    write changes to file

    @path: path to file
    @data: data to be written to file
    """
    def writeToFile(self, path, data):
        # write changes to file
        with open(path, 'w') as file:
            data = json.dumps(data, indent=4)
            file.write(data)

    """
    save school to school file
    """
    def saveSchool(self, schoolName, initials):
        check = False
        fileContent = None
        path = self.paths.get('faculties')

        # check if school/faculty already exists
        if os.path.exists(path):
            with open(path, 'r') as file:
                file = file.read()
                data = json.loads(file)

            for key, value in data.items():
                if initials == key:
                    console.print(f"\nFaculty [yellow italic]{initials}[/yellow italic] already "\
                                  f"exists as [yellow italic]{value}[/yellow italic]\n")
                elif schoolName == value:
                    console.print(f"\nFaculty [yellow italic]{schoolName}[/yellow italic] already "\
                                  f"exists as [yellow italic]{key}[/yellow italic]\n")

                # ask for confirmation to overwrite school
                if initials == key or schoolName == value:
                    while True:
                        confirm = input("Continue to overwrite school? (Y | N)  ").strip().upper()

                        if confirm == "Y":
                            check = True
                            break
                        elif confirm == "N":
                            console.print("[red]Operation Aborted![/red]\n")
                            return
                        else:
                            console.print("[red]Invalid option[red]")

                    if check:
                        break

        # write to file 
        if os.path.exists(path):
            with open(path, 'r') as file:
                file = file.read()
                if file:
                    fileContent = json.loads(file)

            with open(path, 'w') as file:
                data = {initials: schoolName}

                if fileContent:
                    fileContent.update(data)
                    data = json.dumps(fileContent, indent=4)
                else:
                    data = json.dumps(data, indent=4)

                file.write(data)
        else:
            with open(path, 'w') as file:
                data = {initials: schoolName}
                data = json.dumps(data, indent=4)

                file.write(data)

        # print success message
        console.print(f"\nSuccessfully added Faculty; [purple]{initials}"\
                      f"[/purple] - [purple]{schoolName}[/purple]\n")

        # update faculties in other files
        self.updateFaculties(initials)

    """
    add newly added faculty to files that contain them
    """
    def updateFaculties(self, faculty):
        # file paths of files to be updated
        paths = [
            self.paths.get('courses'),
            self.paths.get('programmes'),
            self.paths.get('tests_and_exams')
        ]

        facultyName = faculty
        faculty = {faculty: {}}

        for path in paths:
            # initialize file content
            fileContent = {}
            fileContent.update(faculty)
            
            if os.path.exists(path):
                # read and update file content
                with open(path, 'r') as file:
                    file = file.read()
                    fileContent = json.loads(file)

                    if facultyName in fileContent.keys():
                        return

                    fileContent.update(faculty)

            # write changes to file
            with open(path, 'w') as file:
                fileContent = json.dumps(fileContent, indent=4)
                file.write(fileContent)

    """
    check if given school/faculty exists
    """
    def checkFaculty(self, faculty):
        path = self.paths.get('faculties')
        faculties = self.loadFromFile(path)

        if not faculties:
            return

        for key, value in faculties.items():
            if faculty == key or faculty == value:
                return key

        return

    """
    view available faculties in the school
    """
    def viewFaculties(self):
        path = self.paths.get('faculties')
        faculties = self.loadFromFile(path)
        table = Table(title="Available Faculties")

        if faculties:
            table.add_column("___")

            for key, value in faculties.items():
                table.add_row(key.upper(), value.title())

            console.print("\n", table, "\n")

    """
    check if entered department already exists

    @ depatment: department name to be checked

    return false if it does not
    return error message if it does
    """
    def checkDepartment(self, department):
        path = self.paths.get('programmes')
        data = self.loadFromFile(path)

        if not data:
            return False

        for school, departments in data.items():
            for deptCode, deptInfo in departments.items():
                if department == deptInfo.get('course code'):
                    return "Department/Course code already exists!"

                if department == deptInfo.get('course'):
                    return "Department already exists!"

        return False

    """
    check if input is a valid integer
    @number: number to be checked
    """
    def validateNumber(self, number):
        number = number.strip()

        try:
            number = int(number)
            return number
        except:
            return False

    """
    add new department to programems.json

    @faculty: name of faculty/school to add a department to
    @deptName: name of department/course to be added
    @deptCode: department code or course code to be added
    @deptCutOff: cut off mark for new department to be added
    """
    def addDepartment(self, faculty, deptName, deptCode, deptCutOff):
        path = self.paths.get('programmes')
        programmes = self.loadFromFile(path)

        if programmes:
            newDept = {deptCode: {
                "cut off": deptCutOff,
                "course code": deptCode,
                "course": deptName
            }}

            # update faculty/school with new department/course and save to file
            programmes.get(faculty).update(newDept)
            self.writeToFile(path, programmes)

            # print success  message
            console.print("\n[green]SUCCESS[/green]\n\nAdded department with info:\n"\
                          f"Name: {deptName.title()}\nCode: {deptCode.upper()}\nCut off mark: {deptCutOff}\n"\
                          f"School: {faculty.upper()}\n")

            # update other storage files with new department

            # --- start update for courses.json

            path = self.paths.get('courses')

            deptInfo = {}

            # create department dictionary containing all levels
            for level in range(100, 600, 100):
                level = str(level)

                if level == '400':
                    deptInfo.update({
                        level: {
                            'first semester': {
                                'total units': None,
                                'total courses': None,
                                'courses': {}
                            }
                        }
                    })
                    continue

                deptInfo.update({
                    level: {
                        'first semester': {
                            'total units': None,
                            'total courses': None,
                            'courses': {}
                        },
                        'second semester': {
                            'total units': None,
                            'total courses': None,
                            'courses': {}
                        }
                    }
                })

            with open(path, 'r') as file:
                file = file.read()
                fileData = json.loads(file)

                # abort if department already exists in faculty
                if deptCode in fileData.get(faculty).keys():
                    return

                # update file object with new department
                fileData.get(faculty).update({deptCode.lower(): deptInfo})

            # write changes to file
            self.writeToFile(path, fileData)

            # --- end update for courses.json

            # --- start update for tests_and_exams.json
            # --- end update for tests_and_exams.json

    """
    check if a given shcool/faculty is empty
    """
    def checkNotEmptyFaculty(self, faculty=None):
        if not faculty:
            return

        path = self.paths.get('courses')
        courses = self.loadFromFile(path)

        if faculty in courses.keys():
            if not courses.get(faculty):
                return True

        return

    """
    delete faculty from files
    """
    def deleteFaculty(self, faculty):
        paths = [
            self.paths.get('courses'),
            self.paths.get('faculties'),
            self.paths.get('programmes'),
            self.paths.get('tests_and_exams')
        ]

        for path in paths:
            # check if file exists
            if not os.path.exists(path):
                continue

            # load file content
            with open(path, 'r') as file:
                fileContent = file.read()
                fileContent = json.loads(fileContent)

            # delete school and write changes to gile if file not empty
            if fileContent:
                fileContent.pop(faculty)

                # write to file
                with open(path, 'w') as file:
                    fileContent = json.dumps(fileContent, indent=4)
                    file.write(fileContent)
                

# create class instance
Utils = Utils()
