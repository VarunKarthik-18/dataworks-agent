import requests

api_url = "https://jsonplaceholder.typicode.com/posts"
response = requests.get(api_url)

if response.status_code == 200:
    print("API Request was successful!")
    print(response.text[:200])  # Print the first 200 characters of the response
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
