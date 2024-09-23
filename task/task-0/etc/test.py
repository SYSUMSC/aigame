import requests
import json

# TODO! write your test answer
url = "http://localhost:5001/rank"
answer = json.load(open("etc/answer.json", "r"))

response = requests.post(url, json=answer)

print(response.json())
