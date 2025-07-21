# standard library imports
import json, re, hashlib, string, os
import PyPDF2

# third party imports
from typing import Union
from pathlib import Path
from rich.table import Table
from rich.console import Console

# constants
CONSOLE = Console()
ACCEPTED_EXTENSIONS = ['.txt', '.csv', '.pdf']


class Utils:
    """
    utility class containing helper functions
    """

    def __init__(self) -> None:
        self.paths = {
            "db": "./src/storage/db.json",
            "courses": "./src/storage/courses.json",
            "faculties": "./src/storage/faculties.json",
            "admin_logs": "./src/storage/admin_logs.txt",
            "programmes": "./src/storage/programmes.json",
            "tests_and_exams": "./src/storage/tests_and_exams.json",
            "states_and_cities": "./src/misc/states_and_cities.json"
        }

    def load_programmes(self) -> list:
        """
        load available programmes in the university
        """

        path = self.paths.get('programmes')
        ret_val = self.load_from_file(path)

        # return content of function call
        return ret_val

    def load_courses(self, student_info: dict = None) -> list:
        """
        load courses for given department and level
        """

        path = self.paths.get('courses')
        ret_val = self.load_from_file(path)

        if student_info:
            school = student_info.get('school')
            level = str(student_info.get('level'))
            department = student_info.get('course_code').lower()

            ret_val = ret_val.get(school).get(department).get(level)

        # return courses for current student
        return ret_val

    def load_states(self, key: str = None) -> list:
        """
        load states and cities in Nigeria
        """

        path = self.paths.get('states_and_cities')
        ret_val = self.load_from_file(path)

        if key:
            ret_val = [item[key] for item in ret_val]

        # return content of function call
        return ret_val

    def load_from_file(self, path: str = None) -> list:
        """
        load data from specified file path
        
        @path: file path for data to be loaded
        """

        if not path:
            return []

        try:
            with open(path, 'r') as file:
                data = file.read()
                data = json.loads(data)
                return data
        except FileNotFoundError:
            return []

    def is_valid_email(self, email: str = None) -> Union[str, None]:
        """
        Utility function to validate email addresses
        """

        if not email:
            return

        email_pattern = r'^[a-z0-9._%+-]{3,}@[a-z0-9.-]+\.[a-z]{2,}$'
        return re.match(email_pattern, email) is not None

    def ensure_unique_email(self, email: str = None) -> None:
        """
        ensure a user hasn't applied with given email
        """
        
        database = self.load_from_file(self.paths.get('db'))

        if not database or not email:
            return
        
        db_ids = database.get("admission_applications")
        db_emails = []

        # return if no key found
        if not db_ids:
            return

        for key, value in db_ids.items():
            if "email" in value:
                db_emails.append(value["email"])
            
        while email in db_emails:
            CONSOLE.print(f"[red]\b{email} already exists[/red]")
            email = input("Enter your email address: ").strip()

    def view_programmes(self) -> None:
        """
        view programmes on offer by the school
        """

        program_info = self.load_programmes()

        # check if file is programme was loaded
        if not program_info:
            CONSOLE.print("[yellow]There are no programmes yet![/yellow]")
            return

        schools = program_info.keys()

        print("\nHere's a list of available programmes:")
        CONSOLE.print(f"\n[purple]SCHOOLS:\t\t"\
                      "DEPARTMENTS:[/purple]")

        for x in schools:
            # get school dict
            school = program_info.get(x)

            # print school/faculty name
            CONSOLE.print(f"\n[green]{x.upper()}[/green]")

            for y in school:
                # get department dict
                dept = school.get(y)

                # get department and course code for printing
                dept_name = dept.get('course')
                course_code = dept.get('course_code')

                # print departments in the school
                print(f"\t\t\t({course_code.upper()}) - {dept_name.title()}")

    def root_admin(self) -> dict:
        """
        create root admin
        """

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

    def logout(self, handle) -> None:
        """
        log the current user out of the portal
        """

        if not handle:
            return

        if not handle.logged_in:
            CONSOLE.print("\n[red]ERROR[/red]\nYou need"\
                          " to be logged in to log out!\n")
        else:
            handle.user = None
            handle.logged_in = None
            handle.logged_in_user = None
            handle.prompt = handle.default_prompt

    def clean_string(self, string: str = None) -> Union[str, None]:
        """
        purge given string of excess whitespace
        """

        if not string:
            return

        string = string.split()
        string = " ".join(string)

        return string

    def validate_name(self, name: str = None) -> Union[str, None]:
        """
        validate given name
        """

        if not name:
            return "Error"

        alphanumeric = "-'"
        letters = string.ascii_letters

        # valid characters
        accepted_characters = f"{letters}{alphanumeric}"

        # check for whitespace in naem
        name = self.clean_string(name)
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
            if character not in accepted_characters:
                return "Invalid character in name!"

        # return None if no issue was found with name
        return 

    def validate_username(self, username: str = None) -> Union[str, None]:
        """
        validate username
        """

        if not username:
            return "Error"

        alphanumeric = "-_."
        letters = string.ascii_letters
        username = self.clean_string(username)

        # valid characters
        accepted_characters = f"{letters}{alphanumeric}"

        # check for whitespace
        if " " in username:
            return "username cannot contain whitespace"

        # check accepted characters
        for character in username:
            if character not in accepted_characters:
                return f"Invalid character `{character}` in username!"

        # return None if no issue was found with username
        return

    def validate_password(self, password: str = None) -> Union[str, None]:
        """
        validate password
        """

        if not password:
            return "Error"

        password = password.strip()

        # check minimum length
        if len(password) < 6:
            return "Password must be at least 6 characters long"

        # return false if no issues found with password
        return

    def write_to_file(self, path: str = None, data: dict = None) -> None:
        """
        write changes to file
        
        @path: path to file
        @data: data to be written to file
        """

        if not path or not data:
            return

        # write changes to file
        with open(path, 'w') as file:
            data = json.dumps(data, indent=4)
            file.write(data)

    def save_school(self, school_name: str = None, initials: str = None) -> None:
        """
        save school to school file
        """

        if not school_name or not initials:
            return

        check = False
        file_content = None
        path = self.paths.get('faculties')

        # check if school/faculty already exists
        if os.path.exists(path):
            with open(path, 'r') as file:
                file = file.read()
                data = json.loads(file)

            for key, value in data.items():
                if initials == key:
                    CONSOLE.print(f"\nFaculty [yellow italic]{initials}[/yellow italic] already "\
                                  f"exists as [yellow italic]{value}[/yellow italic]\n")
                elif school_name == value:
                    CONSOLE.print(f"\nFaculty [yellow italic]{school_name}[/yellow italic] already "\
                                  f"exists as [yellow italic]{key}[/yellow italic]\n")

                # ask for confirmation to overwrite school
                if initials == key or school_name == value:
                    while True:
                        confirm = input("Continue to overwrite school? (Y | N)  ").strip().upper()

                        if confirm == "Y":
                            check = True
                            break
                        elif confirm == "N":
                            CONSOLE.print("[red]Operation Aborted![/red]\n")
                            return
                        else:
                            CONSOLE.print("[red]Invalid option[red]")

                    if check:
                        break

        # write to file 
        if os.path.exists(path):
            with open(path, 'r') as file:
                file = file.read()
                if file:
                    file_content = json.loads(file)

            with open(path, 'w') as file:
                data = {initials: school_name}

                if file_content:
                    file_content.update(data)
                    data = json.dumps(file_content, indent=4)
                else:
                    data = json.dumps(data, indent=4)

                file.write(data)
        else:
            with open(path, 'w') as file:
                data = {initials: school_name}
                data = json.dumps(data, indent=4)

                file.write(data)

        # print success message
        CONSOLE.print(f"\nSuccessfully added Faculty; [purple]{initials}"\
                      f"[/purple] - [purple]{school_name}[/purple]\n")

        # update faculties in other files
        self.update_faculties(initials)

    def update_faculties(self, faculty: str = None) -> None:
        """
        add newly added faculty to files that contain them
        """

        if not faculty:
            return

        # file paths of files to be updated
        paths = [
            self.paths.get('courses'),
            self.paths.get('programmes'),
            self.paths.get('tests_and_exams')
        ]

        faculty_name = faculty
        faculty = {faculty: {}}

        # --- structure for tests and exams
        tne_structure = {faculty_name: {}}

        for level in range(100, 600, 100):
            if level == 400:
                tne_structure[faculty_name].update({
                    level: {
                        "tests": {
                            "first_semester": {},
                        },
                        "exams": {
                            "first_semester": {},
                        }
                    }
                })
            else:
                tne_structure[faculty_name].update({
                    level: {
                        "tests": {
                            "first_semester": {},
                            "second_semester": {}
                        },
                        "exams": {
                            "first_semester": {},
                            "second_semester": {}
                        }
                    }
                })
        # --- end structure for tests and exams

        for path in paths:
            # initialize file content
            file_content = {}

            # reset file content for tests and exams
            if path == self.paths.get('tests_and_exams'):
                file_content = tne_structure
            else:
                file_content.update(faculty)

            if os.path.exists(path):
                # read and update file content
                with open(path, 'r') as file:
                    file = file.read()
                    file_content = json.loads(file)

                    if faculty_name in file_content.keys():
                        return

                    # update with different dictionary for tests and exams
                    if path == self.paths.get('tests_and_exams'):
                        file_content.update(tne_structure)
                    else:
                        file_content.update(faculty)

            # write changes to file
            with open(path, 'w') as file:
                file_content = json.dumps(file_content, indent=4)
                file.write(file_content)

    def check_faculty(self, faculty: str = None) -> Union[None, str]:
        """
        check if given school/faculty exists
        """

        if not faculty:
            return

        path = self.paths.get('faculties')
        faculties = self.load_from_file(path)

        if not faculties:
            return

        for key, value in faculties.items():
            if faculty == key or faculty == value:
                return key

        return

    def view_faculties(self) -> None:
        """
        view available faculties in the school
        """

        path = self.paths.get('faculties')
        faculties = self.load_from_file(path)
        table = Table(title="Available Faculties")

        if faculties:
            table.add_column("___")

            for key, value in faculties.items():
                table.add_row(key.upper(), value.title())

            CONSOLE.print("\n", table, "\n")

    def check_department(self, department: str = None, verbose: str = True) \
            -> Union[None, str]:
        """
        check if entered department already exists
        
        @ depatment: department name to be checked
        @verbose: return department key if false
        
        return false if it does not
        return error message if it does
        """

        path = self.paths.get('programmes')
        data = self.load_from_file(path)

        if not data or not department:
            return "Error"

        for school, departments in data.items():
            for dept_code, dept_info in departments.items():
                if department == dept_info.get('course_code') or \
                   department == dept_info.get('course'):

                    # dont return verbose message if verbose false
                    if not verbose:
                        return dept_info.get('course_code')

                    return "Department/Course code already exists!"

        return

    def validate_number(self, number) -> Union[int, None]:
        """
        check if input is a valid integer
        @number: number to be checked
        """

        if not number:
            return

        number = number.strip()

        try:
            number = int(number)
            return number
        except:
            return None

    def add_department(self, faculty: str = None, \
                       dept_name: str = None, \
                       dept_code: str = None, \
                       dept_cut_off: str = None) -> None:
        """
        add new department to programems.json

        @faculty: name of faculty/school to add a department to
        @dept_name: name of department/course to be added
        @dept_code: department code or course code to be added
        @dept_cut_off: cut off mark for new department to be added
        """

        if not faculty or not dept_name or not \
           dept_code or not dept_cut_off:
            return

        path = self.paths.get('programmes')
        programmes = self.load_from_file(path)

        if programmes:
            new_dept = {dept_code: {
                "cut_off": dept_cut_off,
                "course_code": dept_code,
                "course": dept_name
            }}

            # update faculty/school with new department/course and save to file
            programmes.get(faculty).update(new_dept)
            self.write_to_file(path, programmes)

            # print success  message
            CONSOLE.print("\n[green]SUCCESS[/green]\n\nAdded department with info:\n"\
                          f"Name: {dept_name.title()}\nCode: {dept_code.upper()}\nCut off mark: {dept_cut_off}\n"\
                          f"School: {faculty.upper()}\n")

            # update other storage files with new department

            # --- start update for courses.json

            path = self.paths.get('courses')
            dept_info = {}

            # create department dictionary containing all levels
            for level in range(100, 600, 100):
                level = str(level)

                if level == '400':
                    dept_info.update({
                        level: {
                            'first_semester': {
                                'total_units': None,
                                'total_courses': None,
                                'courses': {}
                            }
                        }
                    })
                    continue

                dept_info.update({
                    level: {
                        'first_semester': {
                            'total_units': None,
                            'total_courses': None,
                            'courses': {}
                        },
                        'second_semester': {
                            'total_units': None,
                            'total_courses': None,
                            'courses': {}
                        }
                    }
                })

            with open(path, 'r') as file:
                file = file.read()
                file_data = json.loads(file)

                # abort if department already exists in faculty
                if dept_code in file_data.get(faculty).keys():
                    return

                # update file object with new department
                file_data.get(faculty).update({dept_code.lower(): dept_info})

            # write changes to file
            self.write_to_file(path, file_data)

            # --- end update for courses.json

    def check_not_empty_faculty(self, faculty: str = None) -> Union[True, None]:
        """
        check if a given shcool/faculty is empty
        """

        if not faculty:
            return

        path = self.paths.get('courses')
        courses = self.load_from_file(path)

        if faculty in courses.keys():
            if not courses.get(faculty):
                return True

        return
    
    def prompt_file_selection(self) -> Union[None, str]:
        """
        prompt user to select file
        """

        CONSOLE.print("\n[blue]Select a file containing matric numbers[/blue]")
        CONSOLE.print(f"[green]Accepted formats:[/green] {', '.join(ACCEPTED_EXTENSIONS)}")
        CONSOLE.print("[dim]Hint: Drag and drop the file or paste the full path.[/dim]\n")

        file_path = input("Enter file path: ").strip().strip('"')

        if not os.path.isfile(file_path):
            CONSOLE.print(f"[red]File not found: {file_path}[/red]")
            return

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ACCEPTED_EXTENSIONS:
            CONSOLE.print(f"[red]Invalid file type: {ext}[/red]")
            return

        return file_path

    def extract_matric_numbers(self, file_path: str = None) -> Union[None, list]:
        """
        extract matric no. from file
        """

        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()
        matric_nos = []

        try:
            if ext in ['.txt', '.csv']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    matric_nos = [line.strip() for line in lines if line.strip()]
            elif ext == '.pdf':
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            for line in text.splitlines():
                                if line.strip():
                                    matric_nos.append(line.strip())
        except Exception as e:
            CONSOLE.print(f"[red]Error reading file: {e}[/red]")
            return []

        return matric_nos
        
    def delete_faculty(self, faculty: str = None) -> None:
        """
        delete faculty from files
        """

        if not faculty:
            return

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
                file_content = file.read()
                file_content = json.loads(file_content)

            # delete school and write changes to gile if file not empty
            if file_content and file_content.get(faculty):
                file_content.pop(faculty)

                # write to file
                with open(path, 'w') as file:
                    file_content = json.dumps(file_content, indent=4)
                    file.write(file_content)

    def delete_department(self, department: str = None) -> None:
        """
        delete department from files
        """

        if not department:
            return

        paths = [
            self.paths.get('courses'),
            self.paths.get('programmes'),
            self.paths.get('tests_and_exams')
        ]

        for path in paths:
            # check if file exists
            if not os.path.exists(path):
                continue

            # load file content
            with open(path, 'r') as file:
                file_content = file.read()
                file_content = json.loads(file_content)

            # delete school and write changes to gile if file not empty
            if file_content:
                for key, value in file_content.items():
                    if not value:
                        continue

                    if department in value.keys():
                        file_content[key].pop(department)

                # write to file
                with open(path, 'w') as file:
                    file_content = json.dumps(file_content, indent=4)
                    file.write(file_content)

    def check_course(self, course: str = None) -> Union[None, str]:
        """
        check if given course exists in any department in school
        """

        courses = self.load_from_file(self.paths.get('courses'))

        if not courses or not course:
            return

        for school, school_info in courses.items():
            for dept, dept_info in school_info.items():
                for level, level_info in dept_info.items():
                    for semester, semester_info in level_info.items():
                        # check course
                        if course in semester_info.get("courses", {}).keys():
                            return course

        return

# create class instance
Utils = Utils()
