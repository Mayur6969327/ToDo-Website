import csv
import os
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

USERS_FILE = 'users.csv'
TASKS_FILE = 'tasks.csv'
DATE_FORMAT = "%Y-%m-%d"
password_reset_attempts = {}

def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users[row['username']] = row
    return users

def save_users(users):
    with open(USERS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['username', 'password', 'security_question', 'security_answer'])
        writer.writeheader()
        for u in users.values():
            writer.writerow(u)

def load_tasks():
    tasks = []
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tasks.append(row)
    return tasks

def save_tasks(tasks):
    with open(TASKS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['username', 'task', 'due_date', 'priority', 'completed'])
        writer.writeheader()
        for task in tasks:
            writer.writerow(task)

def get_current_user():
    return session.get('username')

@app.route('/')
def home():
    return redirect(url_for('dashboard') if get_current_user() else url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if not user or not check_password_hash(user['password'], password):
            flash('Invalid credentials', 'danger')
            return render_template('login.html')
        session['username'] = username
        flash(f'Welcome back, {username}!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username'].strip()
        password = request.form['password']
        confirm = request.form['confirm_password']
        question = request.form['security_question']
        answer = request.form['security_answer'].lower()

        if username in users:
            flash('Username taken.', 'danger')
            return render_template('signup.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html')

        users[username] = {
            'username': username,
            'password': generate_password_hash(password),
            'security_question': question,
            'security_answer': answer
        }
        save_users(users)
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    username = get_current_user()
    if not username:
        return redirect(url_for('login'))

    tasks = load_tasks()
    user_tasks = [t for t in tasks if t['username'] == username]

    sort_by = request.args.get('sort_by', '')

    if sort_by == 'due_date':
        user_tasks.sort(key=lambda t: t['due_date'] or '')
    elif sort_by == 'priority':
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        user_tasks.sort(key=lambda t: priority_order.get(t['priority'], 3))

    total = len(user_tasks)
    completed = sum(t['completed'] == 'True' for t in user_tasks)
    pending = total - completed

    today = datetime.today()
    reminders = [f"'{t['task']}' is due tomorrow!" for t in user_tasks
                 if t['due_date'] and
                    0 <= (datetime.strptime(t['due_date'], DATE_FORMAT) - today).days <= 1
                 and t['completed'] == 'False']

    return render_template('dashboard.html',
                           total_tasks=total,
                           completed_tasks=completed,
                           pending_tasks=pending,
                           reminders=reminders,
                           tasks=user_tasks,
                           sort_by=sort_by,
                           notifications=[])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = get_current_user()
    if not username:
        return redirect(url_for('login'))
    users = load_users()
    user = users.get(username)
    return render_template('profile.html', username=username, question=user['security_question'])

@app.route('/reset_password', methods=['POST'])
def reset_password():
    username = get_current_user()
    if not username:
        return redirect(url_for('login'))
    users = load_users()
    new = request.form['new_password']
    confirm = request.form['confirm_password']
    if new != confirm:
        flash("Passwords do not match", 'danger')
        return redirect(url_for('profile'))
    users[username]['password'] = generate_password_hash(new)
    save_users(users)
    flash("Password reset successful", 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    username = get_current_user()
    if not username:
        return redirect(url_for('login'))
    users = load_users()
    user = users.get(username)

    answer = request.form['security_answer'].strip().lower()
    global password_reset_attempts
    now = time.time()
    attempts, last_failed = password_reset_attempts.get(username, (0, 0))

    if attempts >= 3 and now - last_failed < 600:
        wait = int(600 - (now - last_failed))
        flash(f"Too many failed attempts. Try after {wait} seconds.", 'danger')
        return redirect(url_for('profile'))

    if answer != user['security_answer']:
        attempts += 1
        password_reset_attempts[username] = (attempts, now)
        left = 3 - attempts
        flash(f"Wrong answer. Attempts left: {left}", 'danger')
        return redirect(url_for('profile'))

    password_reset_attempts.pop(username, None)
    users.pop(username)
    save_users(users)
    tasks = [t for t in load_tasks() if t['username'] != username]
    save_tasks(tasks)
    session.pop('username')
    flash('Account deleted.', 'info')
    return redirect(url_for('signup'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out", "info")
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_task():
    username = get_current_user()
    if not username:
        return redirect(url_for('login'))

    task = request.form['task']
    due_date = request.form['due_date']
    priority = request.form['priority']
    new_task = {
        'username': username,
        'task': task,
        'due_date': due_date,
        'priority': priority,
        'completed': 'False'
    }
    tasks = load_tasks()
    tasks.append(new_task)
    save_tasks(tasks)
    flash('Task added successfully.', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
