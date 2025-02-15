import datetime
import logging
import os
import re
import sqlite3
import json
import numpy as np
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, APIRouter
from sentence_transformers import SentenceTransformer
import subprocess

# Initialize FastAPI app first
app = FastAPI()
router = APIRouter()

# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def install_and_run(email: str):
    # Implementation for installing and running datagen
    subprocess.run(["pip", "install", "datagen"], check=True)
    subprocess.run(["datagen", "--email", email], check=True)
    return "Datagen installed and run successfully"

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
        
        with open(output_path, 'w') as f:
            f.write("\n".join(filtered_dates))
        
        return f"Found {len(filtered_dates)} dates matching weekday {weekday} and saved to {output_path}"
    except Exception as e:
        logging.error(f"Error in counting weekdays: {e}")
        raise HTTPException(status_code=500, detail=f"Error in counting weekdays: {str(e)}")

def is_valid_weekday(date_str, weekday):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date().weekday() == weekday
    except ValueError:
        return False

def sort_contacts():
    with open("data/contacts.json", "r") as f:
        contacts = json.load(f)
    contacts.sort(key=lambda x: (x["last_name"], x["first_name"]))
    with open("data/contacts-sorted.json", "w") as f:
        json.dump(contacts, f, indent=4)
    return "Contacts sorted and saved."

def handle_a5():
    log_files = sorted(Path("data/").glob("*.log"), key=os.path.getmtime, reverse=True)
    if not log_files:
        return "No log files found."
    with open(log_files[0], "r") as f:
        first_line = f.readline().strip()
    with open("data/logs-recent.txt", "w") as f:
        f.write(first_line)
    return "Extracted first line from most recent log."

def format_markdown(file_path: str):
    subprocess.run(["prettier", "--write", file_path], check=True)
    return "Markdown formatted successfully."

def extract_h1_index():
    with open("data/format.md", "r") as f:
        content = f.read()
    headers = re.findall(r"^# (.+)$", content, re.MULTILINE)
    with open("data/index.md", "w") as f:
        for i, header in enumerate(headers, 1):
            f.write(f"{i}. {header}\n")
    return "Created markdown index from H1 headers"

def query_gold_ticket_sales(db_path: str, output_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(price) FROM tickets WHERE category = 'Gold'")
    total_sales = cursor.fetchone()[0] or 0
    with open(output_path, "w") as f:
        f.write(str(total_sales))
    conn.close()
    return f"Total Gold ticket sales: {total_sales}"

def generate_word_embeddings(input_path: str, output_path: str):
    with open(input_path, "r") as f:
        sentences = [line.strip() for line in f.readlines()]
    embeddings = embedding_model.encode(sentences).tolist()
    with open(output_path, "w") as f:
        json.dump(embeddings, f)
    return "Generated word embeddings."

def extract_emails(input_path: str, output_path: str):
    with open(input_path, "r") as f:
        content = f.read()
    emails = list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", content)))
    with open(output_path, "w") as f:
        f.write("\n".join(emails))
    return "Extracted emails saved."

def find_similar_comments():
    with open("data/comments.txt", "r") as f:
        comments = [line.strip() for line in f.readlines()]
    
    embeddings = embedding_model.encode(comments)
    
    similar_pairs = []
    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            similarity = np.dot(embeddings[i], embeddings[j]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            )
            if similarity > 0.8:
                similar_pairs.append((comments[i], comments[j], similarity))
    
    with open("data/similar_comments.txt", "w") as f:
        for c1, c2, sim in sorted(similar_pairs, key=lambda x: x[2], reverse=True):
            f.write(f"Similarity: {sim:.2f}\n1: {c1}\n2: {c2}\n\n")
    
    return f"Found {len(similar_pairs)} similar comment pairs"

def execute_task(task: str):
    task_mapping = {
        "install and run datagen": lambda: install_and_run("user@example.com"),
        "run datagen": lambda: install_and_run("user@example.com"),
        "format markdown": lambda: format_markdown("data/format.md"),
        "prettier format": lambda: format_markdown("data/format.md"),
        "count the number of Wednesdays": lambda: count_weekday("data/dates.txt", "data/dates-wednesdays.txt", 2),
        "find Wednesdays": lambda: count_weekday("data/dates.txt", "data/dates-wednesdays.txt", 2),
        "count Wednesdays": lambda: count_weekday("data/dates.txt", "data/dates-wednesdays.txt", 2),
        "sort contacts": lambda: sort_contacts(),
        "sort contact list": lambda: sort_contacts(),
        "extract first line from most recent log": lambda: handle_a5(),
        "get recent logs": lambda: handle_a5(),
        "create markdown index": lambda: extract_h1_index(),
        "extract markdown headers": lambda: extract_h1_index(),
        "extract emails": lambda: extract_emails("data/emails.txt", "data/extracted_emails.txt"),
        "find email sender": lambda: extract_emails("data/emails.txt", "data/extracted_emails.txt"),
        "find similar comments": lambda: find_similar_comments(),
        "compare comments": lambda: find_similar_comments(),
        "total sales for Gold tickets": lambda: query_gold_ticket_sales("data/ticket-sales.db", "data/ticket-sales-gold.txt"),
        "gold ticket sales": lambda: query_gold_ticket_sales("data/ticket-sales.db", "data/ticket-sales-gold.txt"),
        "generate word embeddings": lambda: generate_word_embeddings("data/text_samples.txt", "data/embeddings.json"),
        "create embeddings": lambda: generate_word_embeddings("data/text_samples.txt", "data/embeddings.json")
    }
    task_lower = task.lower().strip()
    if task_lower in task_mapping:
        logging.info(f"Executing task: {task}")
        return task_mapping[task_lower]()
    for key in task_mapping:
        if key in task_lower or task_lower in key:
            logging.info(f"Found similar task '{key}' for input '{task}'")
            return task_mapping[key]()
    logging.error(f"Unsupported task: {task}")
    raise HTTPException(status_code=400, detail=f"Unsupported task. Available tasks are: {', '.join(task_mapping.keys())}")

# Add route to router instead of directly to app
@router.post("/run")
async def run(task: str):
    return execute_task(task)

# Include router in the app
app.include_router(router)
