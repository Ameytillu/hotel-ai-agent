from flask import Flask, render_template, request, jsonify
from agents.sentiment_agent import respond_to_review
from agents.faq_agent import get_best_answer

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_input = data.get("input")
    task = data.get("task")

    if task == "Analyze Review":
        response = respond_to_review(user_input)
    else:
        response = get_best_answer(user_input)

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)