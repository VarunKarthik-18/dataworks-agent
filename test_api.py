import os

output_path = "data/api_response.json"  # Path to save the response

# Check if the directory exists, if not, create it
if not os.path.exists(os.path.dirname(output_path)):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"Created directory: {os.path.dirname(output_path)}")

# Now you can proceed with the API request and file saving
from tasks_phase_b import fetch_api_data

api_url = "https://jsonplaceholder.typicode.com/posts"  # Sample API URL

try:
    print("Starting fetch...")
    result = fetch_api_data(api_url, output_path)
    print(result)
except Exception as e:
    print(f"Error: {e}")
