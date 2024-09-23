from flask import Flask, request, jsonify
from rank import cal_score

app = Flask(__name__)

@app.route('/rank', methods=['POST'])
def calculate_score():
    answer_json = request.get_json()
    if not answer_json:
        return jsonify({"error": "No input data provided"}), 400
    score = cal_score(answer_json)
    return jsonify({"score": score})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
