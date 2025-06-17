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
        return render_template("index.html", tasks = tasks)
        
    elif request.method == "POST":
        title = request.form.get("title")
        priority = request.form.get("priority")

        if not title:
            return "Title is required", 400
        try:
            insert_task(title, priority,)
        except Exception:
            return "Failed to add task.", 500
        return redirect("/tasks")

@app.route("/update/<int:task_id>", methods=["POST"])
def update(task_id):
    title = request.form.get("title")
    priority = request.form.get("priority").strip().lower()
    done = request.form.get("done")

    if done == "on":
        done = 1
    
    else:
        done = 0

    valid_priorities = ["high", "medium", "low"]
    if priority is None or priority not in valid_priorities:
        return "Priority is required and must be High, Medium, or Low.", 400
    try:
        update_task(task_id, title=title, priority=priority, done=done)
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
    

def insert_task(title, priority):
    conn = None
    try:
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        created_at = datetime.now().strftime(("%Y-%m-%d %H:%M"))
        cursor.execute("INSERT INTO tasks (created_at, title,  priority) VALUES (?, ?, ?)", (created_at, title, priority))
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

def update_task(task_id, title=None, priority = None, done = None):
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