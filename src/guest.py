# standard library imports
import random, string, hashlib, datetime, re, json

# third party imports
from typing import Union
from rich.table import Table
from rich.console import Console

# local app imports
from src.user import User
from src.utils import Utils
from src.login import Login

# constants
CONSOLE = Console()

class Guest(User):
    """
    guest class to handle guest native commands
    """

    def __init__(self, main_handle):
        self.guest_commands = {
            'login': self.login,
            'logout': self.logout,
            'apply': self.apply_admission,
            'check status': self.check_status,
            'cancel application': self.cancel_application,
        }

        # call constructor of base class
        super().__init__(main_handle)

        # check if there is a logged in user and set user data
        if self.logged_in:
            self.set_logged_in_data(self.main_handle_dict.get('logged_in_user')['id'])

        # execute given user command
        self.execute_command()

    def execute_command(self) -> None:
        """
        execute user command
        """

        if self.command in self.guest_commands.keys():
            self.guest_commands.get(self.command)()

    def check_status(self) -> None:
        """
        check application_status
        """

        # check if user is logged in first
        if not self.logged_in:
            CONSOLE.print("[red]Oops, you need to be logged in to do that![/red]")
            return

        # check if user has been admitted and start student enrollment
        if self.application_status == 'admitted':
            self.register_student()
        elif self.application_status == 'rejected':
            self.delete_student()
        else:
            CONSOLE.print(f"\nHello, {self.first_name.title()}! \nYour application_status is: "\
                          f"[red]{self.application_status}[/red]\n")

    def delete_student(self) -> None:
        """
        delete rejection student from applications list
        """

        # delete student
        del self.main_handle_dict.get('admission_applications')[self.id]

        # print consolation message
        CONSOLE.print("\n[red]Unfortunately, your application has been rejected![/red]\n\n"\
                      "Sorry to see you go.\nTry again another year, you've got this!\n")

        # log rejected user out
        self.logout()        

    def register_student(self) -> None:
        """
        register newly admitted student
        """

        CONSOLE.print(f"\n[green]CONGRATULATIONS, {self.first_name.title()}![/green] \n\n"\
                      f"Your application is successful!\n")
        table = Table(title="Programme Details")
        table.add_column('___')

        table.add_row("School", self.school.upper())
        table.add_row("Course", self.course_of_choice.title())
        table.add_row("Course Code", self.course_code.upper())
        table.add_row("Matric Number", self.matric_no.upper())

        CONSOLE.print("\n", table, "\n")
        CONSOLE.print("[red bold]Store your matric number safely![/red bold]\n")

        # ask to setup new password for student
        while True:
            confirm = input("Setup new password? [Y | N] : ")
            confirm = Utils.clean_string(confirm).lower()

            if confirm == 'y' or confirm == 'yes':
                password = input("Enter new password: ")
                check = Utils.validate_password(password)

                if not check:
                    # hash password
                    password = hashlib.md5(password.encode())
                    password = password.hexdigest()
                    
                    # set new password for student
                    self.main_handle_dict.get('students').get(self.matric_no)['password'] = password
                    CONSOLE.print("\n[green]Password updated![/green]\n")
                    break
                else:
                    CONSOLE.print(f"\n[red]{check}[/red]\n")
            elif confirm == 'n' or confirm == 'no':
                CONSOLE.print("\n[yellow]You've chosen to keep current password![/yellow]\n")
                break
            else:
                CONSOLE.print("\n[red]ERROR[/red]\nInvalid option chosen!\n")

        CONSOLE.print("[purple]Welcome to our school![/purple]\n"\
                      "[red]Your application account will be deleted[/red]\n")

        # set student setup status for newly registered student
        self.main_handle_dict['students'].get(self.matric_no)['student setup'] = True

        # delete user from application dictionary and logout
        del self.main_handle_dict.get('admission_applications')[self.id]
        self.logout()

    def cancel_application(self) -> None:
        """
        cancel application to school
        """

        # check if user is logged in first
        if not self.logged_in:
            CONSOLE.print("[red]Oops, you need to be logged in to do that![/red]")
            return

        confirmation_keys = ['y', 'n', 'yes', 'no']

        while True:
            confirmation = input(f"Are you sure you want to cancel "
            f"your application? [Y (Yes) | N (No)]:  ")

            try:
                confirmation = str(confirmation).lower()
                
                if confirmation in confirmation_keys:
                    if confirmation == 'y' or confirmation == 'yes':
                        # print goodbye message
                        CONSOLE.print(f"Sorry to see you go, {self.first_name.title()}.\n[blue]"\
                                      f"Goodluck with future applications.[/blue]\n")

                        # delete applicant from student list if already admitted
                        if self.main_handle_dict.get('students') and self.application_status == 'admitted':
                            del self.main_handle_dict['students'][self.matric_no]

                        # delete application from application dictionary and save storage
                        del self.main_handle_dict.get('admission_applications')[self.id]

                        self.logout()
                        break
                    else:
                        CONSOLE.print(f"[yellow]Operation Cancelled![/yellow]")
                        break
                else:
                    CONSOLE.print("[yellow]Invalid value![/yellow]")
            except:
                CONSOLE.print("[yellow]Invalid value![/yellow]")
                continue            

    def get_valid_state(self, prompt: str) -> Union[None, str]:
        """
        validate the state
        """

        while True:
            state = Utils.clean_string(input(prompt).title())

            if state in self.states:
                return state

            CONSOLE.print("\n[yellow]Invalid state. \nPlease enter a valid state.[/yellow]\n")

    def get_valid_course(self) -> None:
        """
        validate course_of_choice
        """

        programmes = Utils.load_programmes()
        school_list = programmes.keys()

        # print available courses in the school
        Utils.view_programmes()

        # get and validate school under which course is
        while True:
            school_name = input("Enter School to apply to: ").lower()
            school_name = Utils.clean_string(school_name)

            if school_name in school_list:
                departments = {}
                school = programmes.get(school_name)

                # get all departments in chosen school
                for key, value in school.items():
                    x = {value.get('course'): value.get('course_code')}
                    departments.update(x)

                # get course if chosen school has departments under it
                if departments:
                    # print courses/departments in chosen school
                    table = Table(title=f"[yellow italic]Courses in {school_name.upper()}[/yellow italic]")
                    table.add_column('___')

                    for dept, code in departments.items():
                        print(departments, dept, code, sep="\n\n")
                        table.add_row(code.upper(), dept.title())

                    CONSOLE.print("\n", table, "\n")

                    while True:
                        course = input("Enter course to apply for: ")
                        course = Utils.clean_string(course).lower()

                        """
                        check if entered course is a department key or value \
                        from dictionary of departments in the chosen school \

                        if it is a key or value:  get the course info \
                        add the school key to it to hold the school name \
                        and instantiate class attribute to hold course info
                        """
                        if course in departments.keys():
                            chosen_course = school.get(departments.get(course))
                            chosen_course.update({'school': school_name})

                            self.chosen_course_info = chosen_course
                            return chosen_course.get('course')
                        elif course in departments.values():
                            # get course info
                            for key, value in departments.items():
                                if value == course:
                                    chosen_course = school.get(course)
                                    chosen_course.update({'school': school_name})

                                    self.chosen_course_info = chosen_course
                                    return chosen_course.get('course')
                        else:
                            CONSOLE.print("\n[red]ERROR[/red]\n"\
                                          "Invalid Course chosen!\n")
                else:
                    CONSOLE.print("\n[yellow]There are no departments"\
                                  " in chosen school, yet.[/yellow]\n")
            else:
                CONSOLE.print("\n[red]ERROR[/red]\n"\
                              "Invalid School\n")

    def get_valid_jamb(self) -> Union[None, int]:
        """
        validate jamb_score of applicant
        """

        # end execution if chosen_course_info dict doesn't exist
        if not self.__dict__.get('chosen_course_info'):
            return

        # get the cut off mark for chosen course
        course_cut_off = self.chosen_course_info.get('cut_off')

        while True:
            try:
                score = int(input("Enter your UTME score: "))
                if 0 <= score <= 400:
                    if score < course_cut_off:
                        CONSOLE.print(f"[yellow]Sorry, your UTME score of "\
                                      f"\b{score} is less than the cut off mark "\
                                      f"\b{course_cut_off}")
                        return
                    else:
                        return score
            except:
                pass

            CONSOLE.print("\n[yellow]Invalid jamb_score.[/yellow]\n"\
                          "Please enter a UTME score between 0 and 400.\n")

    def apply_admission(self) -> None:
        """
        handle admission application for guests
        """

        if not Utils.load_programmes():
            CONSOLE.print("\n[red]ERROR[/red]\nNo programmes available!\n")
            return

        # check and stop user from applying if logged in
        if self.logged_in:
            CONSOLE.print(f"[red]\nOops, you can't apply while logged in!\n[/red]")
            return

        id = f"uid{random.randint(0,9999):04}"

        # ensure generated ID is unique
        while id in self.admission_applications.keys():
            id = f"uid{random.randint(0,9999):04}"

        # randomly generate and hash generated password for user
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        hashed_password = hashlib.md5(password.encode())
        hashed_password = hashed_password.hexdigest()

        # get and check first_name
        while True:
            first_name = input("Enter your First Name: ").strip().lower()
            check = Utils.validate_name(first_name)

            if check:
                CONSOLE.print(f"[red]{check}[/red]")
                continue

            break

        # get and check last_name
        while True:
            last_name = input("Enter your Last Name: ").strip().lower()
            check = Utils.validate_name(last_name)

            if check:
                CONSOLE.print(f"[red]{check}[/red]")
                continue

            break

        # get and check middle_name
        while True:
            middle_name = input("Enter your Middle Name: ").strip().lower()

            if middle_name == "":
                middle_name = None
                break

            check = Utils.validate_name(middle_name)

            if check:
                CONSOLE.print(f"[red]{check}[/red]")
                continue

            break

        email = input("Enter your Email Address: ").strip().lower()

        # validate email
        while not Utils.is_valid_email(email):
            print("Invalid email address. Please enter a valid email.")
            email = input("Enter your Email Address: ").strip().lower()
        
        # ensure email is unique
        Utils.ensure_unique_email(email)
            
        # loading available states as a list from states-and-cities.json
        self.states = Utils.load_states('name')
        self.states = sorted(self.states)

        # print states
        CONSOLE.print("\n[blue]Here are the valid states:[/blue]")
        for state in self.states:
            CONSOLE.print(f"\t- {state}")

        state_of_origin = self.get_valid_state("Enter your State of Origin: ").lower()
        state_of_residence = self.get_valid_state("Enter your State of Residence: ").lower()

        # collect and validate date_of_birth
        while True:
            # collect date_of_birth
            date_of_birth = input("Enter your Date of Birth (DD-MM-YYYY): ")

            if len(date_of_birth) == 8 or len(date_of_birth) == 10:
                # strip possible dashes <-> from date_of_birth
                if '-' in date_of_birth:
                    date_of_birth = date_of_birth.replace('-', '')

                # split date_of_birth into day, month and year
                try:
                    day_of_birth = int(date_of_birth[0:2])
                    month_of_birth = int(date_of_birth[2:4])
                    year_of_birth = int(date_of_birth[4:])
                    current_year = datetime.datetime.now().year

                    # checking if user is within the age limit of 16-30 years
                    if 16 <= (current_year - year_of_birth) <= 30:
                        # make date_of_birth into a datetime object to validate date
                        date_of_birth = datetime.date(year_of_birth, month_of_birth, day_of_birth)
                        break
                    else:
                        CONSOLE.print("\n[yellow]You must be between 16 and "\
                                      "30 years old to apply![/yellow]\n")
                        continue
                except:
                    CONSOLE.print("\n[yellow]Invalid date. "\
                          "\nPlease enter a valid date_of_birth.[/yellow]\n")
                    continue
            else:
                CONSOLE.print("\n[yellow]Oops, invalid value.\nTry again![/yellow]\n")
                continue

        date_of_birth = f"{day_of_birth:02}-{month_of_birth:02}-{year_of_birth}"

        # validate chosen course and jamb_score
        course_of_choice = self.get_valid_course()
        jamb_score = self.get_valid_jamb()

        # cancel application is UTME score is less than cutoff
        if not jamb_score:
            CONSOLE.print("[red]Sorry, you cannot continue with"\
                          " this application!\n[/red]")
            return

        # cast application_date to str to pass json serialization
        application_date = datetime.datetime.now()
        school = self.chosen_course_info.get('school').lower()
        course_code = self.chosen_course_info.get('course_code').lower()

        user_application = {
            id: {
                'id': id,
                'email': email,
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'date_of_birth': date_of_birth,
                'state_of_origin': state_of_origin,
                'state_of_residence': state_of_residence,
                'jamb_score': jamb_score,
                'school': school,
                'course_of_choice': course_of_choice,
                'course_code': course_code,
                'application_date': application_date.strftime("%d-%m-%Y %H:%M:%S"),
                'password': hashed_password,
                'application_status': "pending"
                 }
        }

        self.admission_applications.update(user_application)

        # print confirmation message upon successful application
        CONSOLE.print("\n[green]Congratulations, your application "\
                      "has been successfully received![/green]\n")
        CONSOLE.print(f"Please, take note of your user id and password: "\
                      f"\nID: [yellow]{id}[/yellow]\nPASSWORD: [yellow]{password}[/yellow]\n")

        # save program state after application
        self.main_handle_dict.update(user_application)
        self.main_handle.save_storage()

    def login(self) -> None:
        """
        log the user into the portal
        """

        login = Login(self.main_handle)
        login.login_guest()

    def set_logged_in_data(self, user_id: str) -> None:
        """
        refresh data if user is logged in
        """

        user = self.main_handle_dict['admission_applications'].get(user_id)

        if user:
            # set logged in user value for logged in user
            if not self.main_handle_dict.get('logged_in_user'):
                self.main_handle_dict['logged_in_user'] = user
                self.main_handle_dict['logged_in_user']['id'] = user_id

            self.__dict__.update(user)

            # set main handle class attributes
            self.main_handle.user = 'guest'
            self.main_handle.logged_in = True            
            self.main_handle.prompt = f"[yellow]({user_id.upper()})   [/yellow]"
