import datetime
import logging
import os
import re
import sqlite3
import json
import numpy as np
from pathlib import Path
from typing import List
from fastapi import HTTPException, APIRouter
from sentence_transformers import SentenceTransformer
import subprocess



from tasks_phase_b import convert_markdown_to_html, fetch_api_data


 # Only import install_and_run from main
# app/tasks.py
# app/tasks.py
from app.utils import extract_h1_index, find_similar_comments  # ✅ Fix circular import

def execute_task(task):
    """Handles different tasks."""
    if "extract h1" in task:
        return extract_h1_index("# Sample Heading")
    if "similar comments" in task:
        return find_similar_comments(["Comment 1", "Comment 2"])
    return "Unknown task"




# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

router = APIRouter()

def count_weekday(input_path: str, output_path: str, weekday: int):
    try:
        logging.info(f"Input Path: {input_path}")
        logging.info(f"Output Path: {output_path}")
        logging.info(f"Weekday: {weekday}")
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        with open(input_path, 'r') as f:
            lines = f.readlines()
            logging.info(f"Dates: {lines}")
        
        filtered_dates = [date.strip() for date in lines if is_valid_weekday(date.strip(), weekday)]
        
        with open(output_path, 'w') as out_file:
            out_file.write("\n".join(filtered_dates))
        
        return f"Found {len(filtered_dates)} dates matching weekday {weekday} and saved to {output_path}"
    except Exception as e:
        logging.error(f"Error in counting weekdays: {e}")
        raise HTTPException(status_code=500, detail=f"Error in counting weekdays: {str(e)}")

def is_valid_weekday(date_str, weekday):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date().weekday() == weekday
    except ValueError:
        return False

def extract_error_logs(log_dir="data/logs", output_file="error_logs.txt"):
    if not os.path.exists(log_dir):
        raise FileNotFoundError(f"Log directory not found: {log_dir}")
    
    error_logs = []
    for log_file in os.listdir(log_dir):
        log_path = os.path.join(log_dir, log_file)
        error_logs.extend(read_log_errors(log_path))
    
    if not error_logs:
        return "No error logs found."
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(error_logs))
    
    return f"Extracted {len(error_logs)} error logs to {output_file}"

def read_log_errors(log_path):
    for encoding in ["utf-8", "utf-16"]:
        try:
            with open(log_path, "r", encoding=encoding) as f:
                return [line.strip() for line in f if "ERROR" in line]
        except UnicodeDecodeError:
            continue
    return []

def extract_emails(input_file="emails.txt", output_file="extracted_emails.txt"):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File not found: {input_file}")
    
    with open(input_file, "r", encoding="utf-8") as file:
        emails = re.findall(r"[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,}", file.read())
    
    if not emails:
        return "No emails found."
    
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(emails))
    
    return f"Extracted {len(emails)} emails to {output_file}"

def execute_sql_query(db_path, query, output_file):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"SQL error: {str(e)}")
    
    if not results:
        return "Query executed, but no results found."
    
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(", ".join(map(str, row)) for row in results))
    
    return f"Query results saved to {output_file}"

def query_gold_ticket_sales(db_path="ticket-sales.db", output_file="ticket-sales-gold.txt"):
    return execute_sql_query(db_path, "SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'", output_file)

def sort_contacts():
    input_path = "contacts.json"
    output_path = "sorted_contacts.json"

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            contacts = json.load(file)
        
        sorted_contacts = sorted(contacts, key=lambda c: (c.get("last_name", ""), c.get("first_name", "")))
        
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(sorted_contacts, file, indent=4)
        
        return f"Sorted contacts saved to {output_path}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sorting contacts: {str(e)}")

def generate_word_embeddings(input_file="text_samples.txt", output_file="word_embeddings.npy"):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File not found: {input_file}")
    
    with open(input_file, "r", encoding="utf-8") as file:
        sentences = file.readlines()
    
    embeddings = embedding_model.encode([s.strip() for s in sentences if s.strip()])
    np.save(output_file, embeddings)
    
    return f"Generated embeddings saved to {output_file}"

def handle_a5():
    logs_dir = Path('data/logs')
    log_files = sorted(logs_dir.glob('*.log'), key=lambda f: f.stat().st_mtime, reverse=True)
    
    if log_files:
        recent_log = log_files[0]
        with open(recent_log, 'r') as log_file:
            first_line = log_file.readline()
        with open('logs-recent.txt', 'w') as output_file:
            output_file.write(first_line)
    
    return "Extracted first line from most recent log."


import os
import subprocess
import logging
from fastapi import HTTPException

def format_markdown(input_path="data/format.md"):
    try:
        # Ensure the `data/` directory exists
        if not os.path.exists("data"):
            os.makedirs("data")

        # Ensure the markdown file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Markdown file not found at: {input_path}")

        # Install Prettier locally (if not already installed)
        subprocess.run(["npm", "install", "prettier@3.4.2"], check=True)

        # Use `npx.cmd` for Windows compatibility
        npx_command = "npx.cmd" if os.name == "nt" else "npx"

        # Run Prettier to format the markdown file
        result = subprocess.run(
            [npx_command, "prettier", "--write", input_path],
            capture_output=True,
            text=True,
            check=True
        )

        logging.info(f"Prettier Output: {result.stdout.strip()}")
        return f"✅ Successfully formatted {input_path}"

    except FileNotFoundError as e:
        logging.error(str(e))
        raise HTTPException(status_code=404, detail=str(e))

    except subprocess.CalledProcessError as e:
        logging.error(f"⚠️ Prettier error: {e.stderr or e.stdout}")
        raise HTTPException(status_code=500, detail=f"Prettier error: {e.stderr or e.stdout}")

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

def query_gold_ticket_sales(db_path="data/ticket-sales.db", output_file="data/ticket-sales-gold.txt"):
    try:
        if not os.path.exists(db_path):
            logging.error(f"Database not found at: {db_path}")
            raise FileNotFoundError(f"Database file not found at {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
            result = cursor.fetchone()[0]
            
            if result is None:
                result = 0
                
            with open(output_file, 'w') as f:
                f.write(str(result))
                
            return f"Total Gold ticket sales: {result}"
            
        except sqlite3.Error as e:
            logging.error(f"SQL Error: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            conn.close()
            
    except Exception as e:
        logging.error(f"Error in query_gold_ticket_sales: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    



def install_and_run(email: str):
    """Install UV (if required) and run datagen.py"""
    subprocess.run(["pip", "install", "uv"], check=True)
    subprocess.run(["python", "datagen.py", email], check=True)
    return "✅ Datagen script executed"

    

def execute_task(task: str):
    task_mapping = {
        # A1 - Install and run datagen
        "install and run datagen": lambda: install_and_run("user@example.com"),
        "run datagen": lambda: install_and_run("user@example.com"),
        
        # A2 - Format markdown
        "format markdown": lambda: format_markdown("data/format.md"),
        "prettier format": lambda: format_markdown("data/format.md"),
        
        # A3 - Count weekdays
        "count the number of Wednesdays": lambda: count_weekday("data/dates.txt", "data/dates-wednesdays.txt", 2),
        "find Wednesdays": lambda: count_weekday("data/dates.txt", "data/dates-wednesdays.txt", 2),
        "count Wednesdays": lambda: count_weekday("data/dates.txt", "data/dates-wednesdays.txt", 2),
        
        # A4 - Sort contacts
        "sort contacts": lambda: sort_contacts(),
        "sort contact list": lambda: sort_contacts(),
        
        # A5 - Recent logs
        "extract first line from most recent log": lambda: handle_a5(),
        "get recent logs": lambda: handle_a5(),
        
        # A6 - Extract H1 from markdown
        "create markdown index": lambda: extract_h1_index(),
        "extract markdown headers": lambda: extract_h1_index(),
        
        # A7 - Extract email sender
        "extract emails": lambda: extract_emails("data/email.txt", "data/email-sender.txt"),
        "find email sender": lambda: extract_emails("data/email.txt", "data/email-sender.txt"),
        
        # A8 - Similar comments
        "find similar comments": lambda: find_similar_comments(),
        "compare comments": lambda: find_similar_comments(),
        
        # A9 - SQLite query
        "total sales for Gold tickets": lambda: query_gold_ticket_sales("data/ticket-sales.db", "data/ticket-sales-gold.txt"),
        "gold ticket sales": lambda: query_gold_ticket_sales("data/ticket-sales.db", "data/ticket-sales-gold.txt"),
        
        # A10 - Word embeddings
        "generate word embeddings": lambda: generate_word_embeddings("data/text_samples.txt", "data/embeddings.json"),
        "create embeddings": lambda: generate_word_embeddings("data/text_samples.txt", "data/embeddings.json")
    }
    
    # Convert task to lowercase for case-insensitive matching
    task_lower = task.lower().strip()
    
    # Try to find an exact match first
    if task_lower in task_mapping:
        logging.info(f"Executing task: {task}")
        return task_mapping[task_lower]()
    
    # If no exact match, try to find a partial match
    for key in task_mapping:
        if key in task_lower or task_lower in key:
            logging.info(f"Found similar task '{key}' for input '{task}'")
            return task_mapping[key]()
    
    # If no match found
    logging.error(f"Unsupported task: {task}")
    raise HTTPException(
        status_code=400, 
        detail=f"Unsupported task. Available tasks are: {', '.join(task_mapping.keys())}"
    )