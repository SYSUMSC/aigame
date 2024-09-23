import requests

# TODO! write your test answer
url = "http://localhost:5000/rank"
answer = {
    "answers": []
}

response = requests.post(url, json=answer)

print(response.json())
