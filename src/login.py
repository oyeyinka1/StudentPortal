# standard library imports
import hashlib, json

# third party imports
from typing import Union
from rich.console import Console

# local app imports
from src.utils import Utils

# create CONSOLE instance
CONSOLE = Console()

class Login:
    """
    handle specific user login
    """

    def __init__(self, main_handle) -> None:
        self.main_handle = main_handle
        self.main_handle_dict = main_handle.__dict__

        self.user = self.main_handle_dict.get("user")
        self.students = self.main_handle_dict.get("students")
        self.admission_applications = self.main_handle_dict.get("admission_applications")

    def check_admitted_student(self, user_id: str) -> Union[False, True]:
        """
        check if already admitted user is attempting \
        to login to guest account
        """

        # check if students dictionary exists
        if not self.students:
            return False

        # check if user trying to login has been admitted
        for key, value in self.students.items():
            if value.get('application_id') == user_id and \
               value.get('student_setup'):
                CONSOLE.print("\n[yellow]You have been admitted.\nLogin "\
                              "to your student account using your "\
                              "matriculation number to continue[/yellow]\n")
                return True

        return False
    
    def login_guest(self) -> Union[None, False]:
        """
        log the user into the portal
        """

        user_id = input("Enter your application ID: ")
        user_id = Utils.clean_string(user_id).lower()

        # check if user with user ID has been admitted
        if self.check_admitted_student(user_id):
            return

        password = input("Enter your password: ")
        password = Utils.clean_string(password)

        hashed_password = hashlib.md5(password.encode()).hexdigest()

        if user_id in self.admission_applications:
            user = self.admission_applications[user_id]

            if hashed_password == user['password']:
                # Set login data in main handle
                self.main_handle_dict['logged_in_user'] = user
                self.main_handle_dict['logged_in_user']['id'] = user_id
                self.main_handle_dict['logged_in'] = True
                self.main_handle_dict['user'] = 'guest'
                self.main_handle.prompt = f"[yellow]({user_id.upper()})   [/yellow]"

                CONSOLE.print(f"[green]\n<< Welcome back, {user['first_name'].title()}! >>\n[/green]")
                return True
            else:
                CONSOLE.print("[red]\nInvalid ID or Password[/red]\n")
        else:
            CONSOLE.print("[red]\nInvalid ID or Password[/red]\n")
            return False

    def login_admin(self) -> None:
        """
        """

        pass

    def login_student(self) -> None:
        """
        """

        pass
