import requests

url = "http://localhost:5000/rank"
data = {
    "answers": ["answer1", "answer2", "answer3"]
}

response = requests.post(url, json=data)

print(response.json())
