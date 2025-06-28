# StudentPortal

A mock student portal shell with basic commands and features.

## Features

- **Guest Admission Application:** Apply for admission as a guest user.
- **User Login/Logout:** Secure login and logout functionality for applicants.
- **Application Status Checking:** Check the status of your admission application.
- **Application Cancellation:** Cancel your admission application if needed.
- **Course and State Selection:** Choose from predefined courses and Nigerian states.
- **Data Persistence:** All data is stored in JSON files for easy access and modification.
- **Command-Based Interface:** Interact with the portal using simple commands.
- **Rich CLI Output:** Uses the `rich` library for enhanced terminal output.

## Project Structure

```
StudentPortal/
│
├── main.py
├── requirements.txt
├── README.md
├── Modules/
│   ├── __init__.py
│   ├── FileStorage.py
│   ├── Guest.py
│   ├── utils.py
│   ├── Misc/
│   │   ├── courses.json
│   │   ├── states-and-cities.json
│   └── Storage/
│       └── db.json
└── .gitignore
```

## Usage

### Prerequisites

- Clone the repository:

   ```
   git clone https://github.com/yourusername/StudentPortal.git
   ```
- Python 3.10+
- [rich](https://pypi.org/project/rich/) library

Install dependencies with:

```sh
pip install -r requirements.txt
```

### Running the Application

Start the portal shell:

```sh
python main.py
```

### Available Commands

| Command           | Description                                      |
|-------------------|--------------------------------------------------|
| `apply`           | Start a new admission application as a guest     |
| `login`           | Log in with your application ID and password     |
| `logout`          | Log out of the portal                            |
| `check status`    | Check your application status (after logging in) |
| `cancel application` | Cancel your admission application             |
| `info`            | List all available commands                      |
| `exit`            | Exit the portal shell                            |

## Data Files

- **Admission Applications:** Stored in `Modules/Storage/db.json`
- **Courses:** Defined in `Modules/Misc/courses.json`
- **States and Cities:** Defined in `Modules/Misc/states-and-cities.json`

## Notes

- This project is for demonstration and learning purposes.
- Data is not persisted between sessions unless implemented in `saveStorage()`.

---

Feel free to contribute or suggest improvements!
