from tasks_phase_b import fetch_api_data

api_url = "https://jsonplaceholder.typicode.com/posts"  # Sample API URL
output_path = "data/api_response.json"  # Path to save the response

# Add print statements to check where it might be failing
try:
    print("Starting fetch...")
    result = fetch_api_data(api_url, output_path)
    print(result)
except Exception as e:
    print(f"Error: {e}")
