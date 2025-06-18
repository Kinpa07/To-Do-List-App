from flask import Flask, redirect, render_template, request
import sqlite3
from datetime import datetime

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


app = Flask(__name__)

@app.route("/")
def home():
    return redirect("/tasks")

@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        try:
            tasks = get_all_tasks()
        except Exception:
            return "Failed to retrieve all tasks", 500
        return render_template("index.html", tasks=tasks, error=None, form_data=None, reopen_id=None)

    elif request.method == "POST":
        title = request.form.get("title")
        priority = request.form.get("priority")
        due_date = request.form.get("due_date")

        error = None

        if not title:
            error = "Title is required."

        try:
            if due_date:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%dT%H:%M")
                if due_date_obj.date() < datetime.today().date():
                    error = "Due date cannot be in the past."
        except ValueError:
            error = "Invalid due date format, use YYYY-MM-DDTHH:MM."

        if error:
            try:
                tasks = get_all_tasks()
            except Exception:
                return "Failed to retrieve all tasks", 500
            return render_template("index.html", tasks=tasks, error=error, 
                                   form_data={"title": title, "priority": priority, "due_date": due_date}, reopen_id=None)

        try:
            insert_task(title, priority, due_date)
        except Exception:
            return "Failed to add task.", 500
        return redirect("/tasks")

@app.route("/update/<int:task_id>", methods=["POST"])
def update(task_id):
    title = request.form.get("title")
    priority = request.form.get("priority").strip().lower()
    done = request.form.get("done")
    due_date = request.form.get("due_date")

    if done == "on":
        done = 1
    else:
        done = 0

    valid_priorities = ["high", "medium", "low"]
    error = None

    if not title:
        error = "Title is required."
    elif priority not in valid_priorities:
        error = "Priority must be High, Medium, or Low."
    elif due_date:
        try:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%dT%H:%M")
            if due_date_obj.date() < datetime.today().date():
                error = "Due date cannot be in the past."
        except ValueError:
            error = "Invalid due date format, use YYYY-MM-DDTHH:MM."

    if error:
        try:
            tasks = get_all_tasks()
        except Exception:
            return "Failed to retrieve tasks.", 500
        # Pass submitted form data back to the template for prefilling
        return render_template(
            "index.html",
            tasks=tasks,
            error=error,
            reopen_id=task_id,
            form_data={
                "title": title,
                "priority": priority,
                "due_date": due_date,
                "done": str(done),
            }
        )

    try:
        update_task(task_id, title=title, priority=priority, done=done, due_date=due_date)
    except Exception:
        return "Failed to update task.", 500
    return redirect("/tasks")

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    try:
        delete_task(task_id)
    except Exception:
        return "Failed to delete task." , 500
    return redirect("/tasks")

@app.template_filter('datetimeformat')
def datetimeformat(value):
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M").strftime("%b %d, %Y at %I:%M %p")
    except Exception:
        return value
    

def insert_task(title, priority, due_date):
    conn = None
    try:
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        created_at = datetime.now().strftime(("%Y-%m-%d %H:%M"))
        cursor.execute("INSERT INTO tasks (created_at, title,  priority, due_date) VALUES (?, ?, ?, ?)", (created_at, title, priority, due_date))
        conn.commit()
    except sqlite3.Error as e:
         print(f"Database error: {e}")
         raise
    finally:
        if conn:     
            conn.close()

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

def update_task(task_id, title=None, priority = None, done = None, due_date = None):
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
    


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
