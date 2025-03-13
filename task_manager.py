# task_manager.py
import click
import sqlite3
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks
    (id INTEGER PRIMARY KEY, 
     title TEXT, 
     priority TEXT,
     due_date TEXT,
     completed INTEGER,
     created_at TEXT)
    ''')
    conn.commit()
    return conn

# Command group
@click.group()
def cli():
    """Simple command-line task manager."""
    pass

# Add task command
@cli.command()
@click.argument('title')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']), default='medium')
@click.option('--due', '-d', help='Due date (YYYY-MM-DD)')
def add(title, priority, due):
    """Add a new task."""
    conn = init_db()
    c = conn.cursor()
    created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO tasks (title, priority, due_date, completed, created_at) VALUES (?, ?, ?, ?, ?)',
              (title, priority, due, 0, created))
    conn.commit()
    click.echo(f"Added task: {title}")

# List tasks command
@cli.command()
@click.option('--all', is_flag=True, help='Show completed tasks too')
def list(all):
    """List all tasks."""
    conn = init_db()
    c = conn.cursor()
    
    if all:
        c.execute('SELECT id, title, priority, due_date, completed FROM tasks')
    else:
        c.execute('SELECT id, title, priority, due_date, completed FROM tasks WHERE completed = 0')
        
    tasks = c.fetchall()
    
    if not tasks:
        click.echo("No tasks found!")
        return
        
    click.echo("ID | Title | Priority | Due Date | Status")
    click.echo("-" * 50)
    
    for task in tasks:
        status = "Completed" if task[4] else "Pending"
        click.echo(f"{task[0]} | {task[1]} | {task[2]} | {task[3] or 'N/A'} | {status}")

# Complete task command
@cli.command()
@click.argument('task_id', type=int)
def complete(task_id):
    """Mark a task as completed."""
    conn = init_db()
    c = conn.cursor()
    c.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
    if c.rowcount == 0:
        click.echo(f"No task found with ID {task_id}")
    else:
        conn.commit()
        click.echo(f"Marked task {task_id} as completed!")

if __name__ == '__main__':
    cli()