Task Manager Web App

A simple Flask-based task manager with Bootstrap styling.  
Allows you to add, edit, delete, and filter tasks with priority and due dates.

---

## Features

- Add tasks with title, priority (low, medium, high), due date, and done status  
- Edit existing tasks or cancel edits gracefully  
- Delete tasks with confirmation  
- Filter tasks by status (All, Pending, Done)  
- Responsive layout using Bootstrap cards

---

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yourrepo.git
   cd yourrepo

2. Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. Install dependencies:
pip install -r requirements.txt

4. Run the App
flask run

Usage
Add new tasks in the form at the top

Click Edit on a task to update it

Use the filter dropdown to view all, pending, or done tasks

Click Delete to remove a task (confirmation required)