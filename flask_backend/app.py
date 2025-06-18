from flask import Flask, request, jsonify, render_template
from groq_agent import CreditCardAgent
from database import get_db_connection, fetch_cards
import os

app = Flask(__name__)
agent = CreditCardAgent()

@app.route('/api/start_conversation', methods=['POST'])
def start_conversation():
    user_data = request.json
    session_id = user_data.get('session_id', 'default')
    response = agent.start_conversation(session_id)
    return jsonify({'response': response})

@app.route('/api/answer', methods=['POST'])
def process_answer():
    data = request.json
    session_id = data.get('session_id', 'default')
    user_answer = data.get('answer')
    response, recommendations = agent.process_answer(session_id, user_answer)
    return jsonify({'response': response, 'recommendations': recommendations})

@app.route('/recommendations', methods=['GET'])
def show_recommendations():
    session_id = request.args.get('session_id', 'default')
    recommendations = agent.get_recommendations(session_id)
    return render_template('recommendations.html', recommendations=recommendations)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)