# Smart Deadline Reminder System

An academic-focused productivity tool that helps students stay on top of their exams and assignments by sending timely email reminders.

## Features

- 📅 Add and manage deadlines for exams and assignments
- 📧 Automatic email reminders before deadlines
- 🎯 Categorize deadlines by type (Exam, Assignment, Project, Quiz)
- ⏰ Customizable reminder times
- 📊 Dashboard to view all upcoming deadlines

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite with SQLAlchemy
- **Email:** Flask-Mail
- **Scheduler:** APScheduler

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/rithika5656/Smart-Deadline-Reminder-System.git
   cd Smart-Deadline-Reminder-System
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your email credentials
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Add your email address in the settings
2. Create new deadlines with title, description, due date, and type
3. Set reminder preferences (1 day before, 1 hour before, etc.)
4. Receive email reminders automatically!

## License

MIT License
