from flask import Flask, redirect, render_template, request
import sqlite3
from datetime import datetime

# Initialize the SQLite database and create the tasks table if it doesn't exist
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done BOOLEAN NOT NULL DEFAULT 0,
        priority TEXT,
        due_date TEXT,             
        created_at TEXT NOT NULL          
    )
    ''')
    conn.commit()
    conn.close()

# Retrieve tasks from the database, optionally filtered by completion status
def get_tasks_filtered(status=None):
    conn = None
    try:
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        base_query = "SELECT * FROM tasks"
        if status == "done":
            base_query += " WHERE done = 1"
        elif status == "pending":
            base_query += " WHERE done = 0"
        base_query += " ORDER BY created_at DESC"
        cursor.execute(base_query)
        tasks = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()
    return tasks

app = Flask(__name__)

# Redirect root URL to /tasks
@app.route("/")
def home():
    return redirect("/tasks")

# Handle displaying and creating tasks
@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        # Filter tasks based on status (done or pending)
        status_filter = request.args.get("status")
        try:
            tasks = get_tasks_filtered(status_filter)
        except Exception as e:
            print(f"Error retrieving tasks: {e}")
            return "Failed to retrieve tasks", 500
        return render_template("index.html", tasks=tasks, error=None, form_data=None, reopen_id=None, status_filter=status_filter)

    elif request.method == "POST":
        # Handle task form submission
        title = request.form.get("title")
        priority = request.form.get("priority")
        due_date_str = request.form.get("due_date")

        error = None
        due_date = None

        if not title:
            error = "Title is required."

        if due_date_str and not error:
            try:
                due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M")
                if due_date_obj.date() < datetime.today().date():
                    error = "Due date cannot be in the past."
                else:
                    due_date = due_date_obj.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                error = "Invalid due date format, use YYYY-MM-DDTHH:MM."

        if error:
            try:
                tasks = get_tasks_filtered()
            except Exception as e:
                print(f"Error retrieving tasks while handling form error: {e}")
                tasks = []
            return render_template(
                "index.html",
                tasks=tasks,
                error=error,
                form_data={"title": title, "priority": priority, "due_date": due_date_str},
                reopen_id=None,
                status_filter=None
            )

        # Insert task if no errors
        try:
            insert_task(title, priority, due_date)
        except Exception as e:
            print(f"Error inserting task: {e}")
            return "Failed to add task.", 500

        return redirect("/tasks")

# Handle updating a task
@app.route("/update/<int:task_id>", methods=["POST"])
def update(task_id):
    title = request.form.get("title")
    priority = request.form.get("priority")
    done = request.form.get("done")
    due_date_str = request.form.get("due_date")

    error = None

    if not title:
        error = "Title is required."

    valid_priorities = ["high", "medium", "low"]
    if priority:
        priority = priority.strip().lower()
        if priority not in valid_priorities:
            error = "Priority must be High, Medium, or Low."
    else:
        priority = None

    due_date = None
    if due_date_str:
        try:
            due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M")
            if due_date_obj.date() < datetime.today().date():
                error = "Due date cannot be in the past."
            else:
                due_date = due_date_obj.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            error = "Invalid due date format, use YYYY-MM-DDTHH:MM."

    done_flag = 1 if done == "on" else 0

    if error:
        try:
            tasks = get_all_tasks()
        except Exception:
            return "Failed to retrieve tasks.", 500
        return render_template(
            "index.html",
            tasks=tasks,
            error=error,
            reopen_id=task_id,
            form_data={
                "title": title,
                "priority": priority,
                "due_date": due_date_str,
                "done": done_flag,
            },
            status_filter=None
        )

    try:
        update_task(task_id, title=title, priority=priority, done=done_flag, due_date=due_date)
    except Exception as e:
        print(f"Error updating task: {e}")
        return "Failed to update task.", 500

    return redirect("/tasks")

# Handle deleting a task
@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    try:
        delete_task(task_id)
    except Exception:
        return "Failed to delete task." , 500
    return redirect("/tasks")

# Custom Jinja filter for formatting datetime strings
@app.template_filter('datetimeformat')
def datetimeformat(value):
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M").strftime("%b %d, %Y at %I:%M %p")
    except Exception:
        return value

# Insert a new task into the database
def insert_task(title, priority, due_date):
    conn = None
    try:
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("INSERT INTO tasks (created_at, title,  priority, due_date) VALUES (?, ?, ?, ?)", (created_at, title, priority, due_date))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        if conn:     
            conn.close()

# Get all tasks without filters
def get_all_tasks():
    conn = None
    try:
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()
    return tasks

# Update task fields based on provided values
def update_task(task_id, title=None, priority=None, done=None, due_date=None):
    conn = None
    try:
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()

        fields = []
        values = []

        if title is not None:
            fields.append("title = ?")
            values.append(title)
        if priority is not None:
            fields.append("priority = ?")
            values.append(priority)
        if done is not None:
            fields.append("done = ?")
            values.append(done)
        if due_date is not None:
            fields.append("due_date = ?")
            values.append(due_date)
        if not fields:
            return

        sql = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        values.append(task_id)
        cursor.execute(sql, values)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error {e}")
        raise
    finally:
        if conn:
            conn.close()

# Delete a task from the database
def delete_task(task_id):
    conn = None
    try:
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Run the app and initialize the DB
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
