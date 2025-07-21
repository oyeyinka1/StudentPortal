# local app imports
from src.utils import Utils

class User:
    """
    base/parent class for our distinct user classes
    """

    def __init__(self, main_handle) -> None:
        """
        constructor function \
        instantiates common attributes for \
        inheriting classes \
        """

        self.levels = ['100', '200', '300', '400', '500']

        self.paths = {
            "db": "./src/storage/db.json",
            "courses": "./src/storage/courses.json",
            "faculties": "./src/storage/faculties.json",
            "admin_logs": "./src/storage/admin_logs.txt",
            "programmes": "./src/storage/programmes.json",
            "tests_and_exams": "./src/storage/tests_and_exams.json",
            "states_and_cities": "./src/misc/states_and_cities.json"
        }

        self.main_handle = main_handle
        self.main_handle_dict = main_handle.__dict__

        self.command = self.main_handle_dict.get('command')
        self.logged_in = self.main_handle_dict.get('logged_in')
        self.students = self.main_handle_dict.get('students', {})
        self.admission_applications = self.main_handle_dict.get('admission_applications')

    def logout(self) -> None:
        """
        log the current user out of the portal
        """

        Utils.logout(self.main_handle)
