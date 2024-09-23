import requests

url = "http://localhost:5000/rank"
data = {
    "answers": []
}

response = requests.post(url, json=data)

print(response.json())
