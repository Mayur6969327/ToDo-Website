📋 Todo Web App
A full-featured Flask-based Todo Web App with CSV file storage. Users can register, log in, manage tasks, reset passwords, and delete accounts securely.

🌟 Features
🔐 User Authentication (Signup/Login/Logout)
✅ Add, View, Sort & Filter Tasks
📅 Set Due Dates and Priorities
🔔 Reminders for Tasks Due Tomorrow
🎯 Track Total, Completed, and Pending Tasks
🔄 Reset Password with Security Questions
🗑️ Delete Account (with attempt limits & cooldown)
📁 CSV-based Storage (no database required)

🖥️ Tech Stack
Backend: Flask (Python)
Frontend: HTML, Bootstrap 5
Data Storage: CSV (users.csv, tasks.csv)

📂 Project Structure
todo-web/
├── app.py
├── users.csv
├── tasks.csv
├── requirements.txt
├── Procfile
├── README.md
├── templates/
│   ├── layout.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── profile.html
└── static/
    └── styles.css

📌 Notes
All data is stored in CSV files.
Make sure to keep your users.csv and tasks.csv safe; they contain sensitive information.
The app uses password hashing and limited attempts for account deletion for better security.

📧 Contact
Made with ❤️ by Mayur.
For issues or suggestions, feel free to open an issue or fork the project.

