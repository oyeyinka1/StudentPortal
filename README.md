# StudentPortal

A mock student portal shell with basic commands and features.

## Features

- Guest admission application
- User login/logout
- Application status checking
- Simple in-memory data storage
- Command-based interface

## Usage

1. **Clone the repository:**

   ```
   git clone https://github.com/yourusername/StudentPortal.git
   ```

2. **Navigate to the project directory:**

   ```
   cd StudentPortal
   ```

3. **Run the main application script:**

   ```
   python main.py
   ```

4. **Available Commands:**
   - `apply` &mdash; Start a new admission application as a guest.
   - `login` &mdash; Log in with your application ID and password.
   - `logout` &mdash; Log out of the portal.
   - `checkstatus` &mdash; Check the status of your application (after logging in).

## Notes

- This project is for demonstration and learning purposes.
- Data is not persisted between sessions unless implemented in `saveStorage()`.

---

Feel free to contribute or suggest improvements!
