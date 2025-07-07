# StudentPortal

A mock student portal shell with basic commands and features.

## Features

- **Guest Mode**
  - Apply for admission
  - Check application status
  - Cancel application

- **Admin Mode**
  - Login/logout as admin
  - View all admission applications
  - Admit or reject applicants
  - View all students
  - View school statistics (students per course/school)
  - View admin logs

- **Student Mode**
  - (Planned) Student-specific features

- **General**
  - Command-line shell interface
  - Data persistence using JSON files
  - Rich console output

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
│   ├── Utils.py
│   ├── Misc/
│   │   ├── courses.json
│   │   ├── states-and-cities.json
│   └── Storage/
│       ├── db.json
        └── admin_logs.txt
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

#### Shell Commands

- `info` — List available commands
- `login` — Log in as guest, admin, or student
- `exit` — Exit the shell

#### Guest Commands

- `apply` — Apply for admission
- `check status` — Check your application status
- `cancel application` — Cancel your application
- `logout` — Log out

#### Admin Commands

- `view applications` — View all admission applications
- `admit` — Admit applicants
- `reject` — Reject applicants
- `view students` — View all admitted students
- `school stats` — View statistics by course and school
- `view admin log` — View all admin logs
- `view my log` — View your admin actions
- `logout` — Log out

## Default Admin

- **Username:** `root`
- **Password:** `admin` (hashed in db.json)
- **Email:** `root@fut.com`

## Data Files

- **Admission Applications:** Stored in `Modules/Storage/db.json`
- **Courses:** Defined in `Modules/Misc/courses.json`
- **States and Cities:** Defined in `Modules/Misc/states-and-cities.json`
- **Admin Logs:** Definrd in `Modules/Storage/admin_logs.txt`

## Notes

- This project is for demonstration and learning purposes.
- Data is not persisted between sessions unless implemented in `saveStorage()`.

---

Feel free to contribute or suggest improvements!
