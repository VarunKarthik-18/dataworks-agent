import os
import subprocess
import requests
import markdown
import logging
from fastapi import HTTPException
import sqlite3
from bs4 import BeautifulSoup
from PIL import Image
import csv
import json
from fastapi import FastAPI, File, UploadFile
from typing import List, Optional
from io import StringIO
import whisper
import ctypes
from pydub import AudioSegment

# Ensure logging is configured properly (e.g., in the main script)
logging.basicConfig(level=logging.INFO)

def convert_markdown_to_html(input_path: str, output_path: str):
    """
    Convert markdown file to HTML
    """
    try:
        # Check if the input file exists
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail=f"Markdown file {input_path} not found")
        
        # Read the markdown content from the file
        with open(input_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content)
        
        # Write the HTML content to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logging.info(f"Markdown successfully converted to HTML and saved to {output_path}")
        return "Successfully converted markdown to HTML"
    
    except Exception as e:
        logging.error(f"Error converting markdown to HTML: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to convert markdown to HTML: {str(e)}")


input_path = "data/example.md"  # Make sure this is the correct path
output_path = "data/example.html"  # The output HTML file path

result = convert_markdown_to_html(input_path, output_path)
print(result)


def fetch_api_data(api_url: str, output_path: str):
    """
    Fetch data from API and save to file
    """
    try:
        logging.basicConfig(level=logging.DEBUG)  # Log all messages of level DEBUG and above
        logging.info(f"Fetching data from: {api_url}")
        
        response = requests.get(api_url)
        response.raise_for_status()
        
        logging.info(f"API Response Status: {response.status_code}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        logging.info(f"Data saved to {output_path}")
        return "Successfully fetched API data"
    except Exception as e:
        logging.error(f"Error fetching API data: {str(e)}")
        raise Exception(f"Failed to fetch API data: {str(e)}")

def clone_and_commit_repo(repo_url: str, commit_message: str, clone_dir: str):
    """
    Clone a Git repository and make a commit if there are changes.
    """
    try:
        # Clone the repository if it doesn't already exist
        if not os.path.exists(clone_dir):
            logging.info(f"Cloning repository from {repo_url} into {clone_dir}...")
            subprocess.check_call(['git', 'clone', repo_url, clone_dir])

        # Change working directory to the cloned repo
        os.chdir(clone_dir)

        # Check if there are any changes (uncommitted files)
        status = subprocess.check_output(['git', 'status', '--porcelain']).decode('utf-8')
        if not status:  # No changes to commit
            logging.info("No changes to commit.")
            return "No changes to commit"
        
        # Example: Create a new file or modify an existing one if there are changes
        with open("new_file.txt", "w") as f:
            f.write("This is a new file added via the automation script.")
        
        # Add and commit changes
        subprocess.check_call(['git', 'add', '.'])
        subprocess.check_call(['git', 'commit', '-m', commit_message])
        
        logging.info(f"Successfully committed changes: {commit_message}")
        return "Successfully cloned and committed to the repo"
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Error: {e}")
        return f"Failed to clone and commit: {e}"

# Example Usage
repo_url = "https://github.com/VarunKarthik-18/dataworks-agent.git"  # Replace with your repo URL
commit_message = "Automated commit: added new file"
clone_dir = "C:/Users/B Varun karthik/dataworks-agent/cloned_repo"  # Directory to clone into

# Call the clone_and_commit_repo function
result = clone_and_commit_repo(repo_url, commit_message, clone_dir)
print(result)

import sqlite3
import os

# Path to SQLite database
db_path = r"C:\Users\B Varun karthik\dataworks-agent\data\ticket-sales.db"

# Ensure the directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Connect to SQLite (this will create the file if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the sales table if it already exists to avoid schema mismatch
cursor.execute("DROP TABLE IF EXISTS sales")

# Create the sales table with the correct schema
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        product_name TEXT,
        quantity INTEGER,
        price REAL
    )
""")

# Insert some sample data
cursor.executemany("""
    INSERT INTO sales (product_name, quantity, price) VALUES (?, ?, ?)
""", [
    ("Product A", 10, 99.99),
    ("Product B", 5, 199.99),
    ("Product C", 2, 299.99)
])

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database created and sample data inserted.")

# Example Usage for running SQL query
def run_sql_query(db_path: str, query: str):
    """
    Connect to the SQLite database and run the provided query.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"Running query on {db_path}: {query}")

        # Execute the query
        cursor.execute(query)

        # If the query is a SELECT, fetch the results
        if query.strip().lower().startswith("select"):
            results = cursor.fetchall()
            print(f"Query results: {results}")
            return results

        # Commit changes for non-SELECT queries (INSERT, UPDATE, DELETE)
        conn.commit()
        print("Query executed successfully.")
        return "Query executed successfully."

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return f"SQLite error: {e}"

    finally:
        # Close the connection
        conn.close()

# Example query to select all rows from the sales table
query = "SELECT * FROM sales LIMIT 10;"  # Adjust this based on your database schema

# Call the function
result = run_sql_query(db_path, query)
print(result)

def scrape_website(url: str, output_path: str):
    """
    Scrape data from a website and save it to a file
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Fetch the content of the webpage
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example: Extract all paragraph texts from the page
        paragraphs = soup.find_all('p')
        text_data = "\n".join([p.get_text() for p in paragraphs])

        # Save the scraped data to a file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_data)

        print(f"Scraped data saved to {output_path}")
        return "Successfully scraped data"
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return f"Error fetching webpage: {e}"
    except Exception as e:
        print(f"Error scraping data: {e}")
        return f"Error scraping data: {e}"

# Example Usage
url = 'https://example.com'  # This is a test site
output_path = 'data/scraped_data.txt'  # Path to save the scraped data

# Call the function
result = scrape_website(url, output_path)
print(result)

def compress_and_resize_image(input_image_path: str, output_image_path: str, resize_dimensions=(800, 800), quality=85):
    """
    Compress and resize the image.
    
    :param input_image_path: Path to the input image.
    :param output_image_path: Path to save the compressed and resized image.
    :param resize_dimensions: Tuple with new dimensions (width, height).
    :param quality: Quality for the compressed image (1-100).
    """
    try:
        # Open the input image
        with Image.open(input_image_path) as img:
            # Resize the image using LANCZOS resampling (replaces ANTIALIAS)
            img = img.resize(resize_dimensions, Image.Resampling.LANCZOS)
            
            # Save the resized and compressed image
            img.save(output_image_path, "JPEG", quality=quality)
        
        logging.info(f"Image successfully compressed and resized. Saved to {output_image_path}")
        return "Successfully compressed and resized the image"
    
    except Exception as e:
        logging.error(f"Error compressing and resizing image: {str(e)}")
        return f"Failed to compress and resize image: {str(e)}"

# Example usage
input_image_path = r"C:\Users\B Varun karthik\Pictures\trlzN6b.jpg"  # Your input image path
output_image_path = r"data\compressed_resized_image.jpg"  # Path to save the resized and compressed image

result = compress_and_resize_image(input_image_path, output_image_path)
print(result)



def filter_csv_and_return_json(csv_file: str, filter_column: str, filter_value: str):
    """
    Filters CSV data based on a column and value, then returns the data as JSON.
    """
    try:
        # Check if the CSV file exists
        if not os.path.exists(csv_file):
            raise HTTPException(status_code=404, detail=f"File not found: {csv_file}")

        # Open the CSV file and read its content
        with open(csv_file, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            filtered_data = [
                row for row in csv_reader if row[filter_column] == filter_value
            ]

        # If filtered data is found, return it as JSON
        if filtered_data:
            json_data = json.dumps(filtered_data, indent=4)
            output_path = "data/filtered_data.json"  # Path to save the filtered data
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json_file.write(json_data)
            print(f"Filtered data saved to {output_path}")
            return f"Filtered data saved to {output_path}"

        else:
            raise HTTPException(status_code=404, detail="No matching data found.")
    
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
        return f"Error processing CSV: {str(e)}"

# Example Usage for CSV filtering
csv_file = "C:/Users/B Varun karthik/dataworks-agent/data/sample.csv"
filter_column = "product_name"  # Column to filter by
filter_value = "Product A"  # Value to filter by

# Call the function
result = filter_csv_and_return_json(csv_file, filter_column, filter_value)
print(result)


def setup_ffmpeg_paths():
    """Ensures FFmpeg and FFprobe are correctly set for pydub."""
    ffmpeg_path = r"C:\Program Files\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"
    ffprobe_path = r"C:\Program Files\ffmpeg\ffmpeg-7.1-essentials_build\bin\ffprobe.exe"

    if not os.path.exists(ffmpeg_path) or not os.path.exists(ffprobe_path):
        raise FileNotFoundError("❌ FFmpeg or FFprobe not found. Please check the installation path.")

    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path
    print(f"✅ FFmpeg Path: {AudioSegment.converter}")
    print(f"✅ FFprobe Path: {AudioSegment.ffprobe}")

def convert_mp3_to_wav(mp3_file_path: str) -> str:
    """Convert MP3 file to WAV using pydub and return WAV file path."""
    if not os.path.exists(mp3_file_path):
        raise FileNotFoundError(f"❌ MP3 file not found: {mp3_file_path}")

    wav_file_path = mp3_file_path.replace(".mp3", ".wav")

    try:
        audio = AudioSegment.from_mp3(mp3_file_path)
        audio.export(wav_file_path, format="wav")
        print(f"✅ Successfully converted MP3 to WAV: {wav_file_path}")
        return wav_file_path
    except Exception as e:
        raise RuntimeError(f"❌ Error converting MP3 to WAV: {str(e)}")

def transcribe_audio(mp3_file_path: str, output_text_path: str):
    """
    Transcribes audio from an MP3 file to text using Whisper.

    Args:
        mp3_file_path (str): Path to the MP3 file.
        output_text_path (str): Path to save the transcribed text.
    """
    try:
        setup_ffmpeg_paths()

        # Convert MP3 to WAV
        wav_file_path = convert_mp3_to_wav(mp3_file_path)

        # Load Whisper model
        print("⏳ Loading Whisper model...")
        model = whisper.load_model("base")

        # Transcribe the audio file
        print("⏳ Transcribing audio...")
        result = model.transcribe(wav_file_path)

        # Get the transcribed text
        transcribed_text = result['text']

        # Write the transcribed text to a file
        with open(output_text_path, 'w', encoding='utf-8') as f:
            f.write(transcribed_text)

        print(f"✅ Transcription successful! Saved to {output_text_path}")

        # Cleanup WAV file after transcription
        os.remove(wav_file_path)
        print(f"🗑️ Removed temporary WAV file: {wav_file_path}")

        return "Successfully transcribed MP3 to text."

    except FileNotFoundError as e:
        print(f"❌ {e}")
        return str(e)
    except Exception as e:
        print(f"❌ Error transcribing audio: {str(e)}")
        return f"Error transcribing audio: {str(e)}"

# Example usage
mp3_file_path = r"C:\Users\B Varun karthik\dataworks-agent\data\Under-The-Influence.mp3"
output_text_path = r"C:\Users\B Varun karthik\dataworks-agent\data\transcribed_text.txt"

# Call the function
result = transcribe_audio(mp3_file_path, output_text_path)
print(result)