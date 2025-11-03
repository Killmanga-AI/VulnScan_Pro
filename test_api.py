import requests

# The API endpoint you want to test
url = "http://127.0.0.1:8000/api/scans"

# The JSON body
data = {"target_url": "http://example.com"}

# Make the POST request
response = requests.post(url, json=data)

# Print the response
print(response.json())