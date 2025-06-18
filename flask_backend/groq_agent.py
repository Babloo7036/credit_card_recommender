from groq import Groq
from database import fetch_cards
import json
import os

class CreditCardAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.user_data = {}
        self.questions = [
            "What is your approximate monthly income (in INR)?",
            "What are your primary spending categories (e.g., fuel, travel, groceries, dining)?",
            "What benefits are most important to you (e.g., cashback, travel points, lounge access)?",
            "Do you have any existing credit cards? If yes, which ones?",
            "What is your approximate credit score? (Enter 'unknown' if unsure)"
        ]
        self.current_question_index = {}
        self.cards = fetch_cards()

    def start_conversation(self, session_id):
        self.current_question_index[session_id] = 0
        self.user_data[session_id] = {}
        return self.questions[0]

    def process_answer(self, session_id, answer):
        if session_id not in self.user_data:
            self.user_data[session_id] = {}
        
        current_index = self.current_question_index.get(session_id, 0)
        if current_index == 0:
            self.user_data[session_id]['income'] = int(answer) if answer.isdigit() else 0
        elif current_index == 1:
            self.user_data[session_id]['spending'] = answer.lower().split(',')
        elif current_index == 2:
            self.user_data[session_id]['benefits'] = answer.lower().split(',')
        elif current_index == 3:
            self.user_data[session_id]['existing_cards'] = answer
        elif current_index == 4:
            self.user_data[session_id]['credit_score'] = answer

        current_index += 1
        self.current_question_index[session_id] = current_index

        if current_index < len(self.questions):
            return self.questions[current_index], None
        else:
            recommendations = self.generate_recommendations(session_id)
            return "Here are your personalized credit card recommendations!", recommendations

    def generate_recommendations(self, session_id):
        user = self.user_data.get(session_id, {})
        recommendations = []
        for card in self.cards:
            score = 0
            reasons = []
            
            # Income eligibility
            if user.get('income', 0) >= card['eligibility_income']:
                score += 30
                reasons.append("Matches your income level")
            
            # Spending match
            if user.get('spending'):
                for spend in user['spending']:
                    if spend.strip() in card['perks'].lower():
                        score += 20
                        reasons.append(f"Supports your {spend.strip()} spending")
            
            # Benefits match
            if user.get('benefits'):
                for benefit in user['benefits']:
                    if benefit.strip() in card['perks'].lower() or benefit.strip() in card['reward_type'].lower():
                        score += 25
                        reasons.append(f"Offers {benefit.strip()} benefits")
            
            # Credit score (if known)
            if user.get('credit_score', 'unknown') != 'unknown' and int(user.get('credit_score', 0)) > 700:
                score += 25
                reasons.append("Suitable for your credit score")

            recommendations.append({
                'name': card['name'],
                'issuer': card['issuer'],
                'score': score,
                'reasons': ", ".join(reasons),
                'rewards_simulation': f"Rs. {int(user.get('income', 0) * card['reward_rate'] / 100 * 12)}/year {card['reward_type'].lower()}"
            })
        
        recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)[:3]
        return recommendations

    def get_recommendations(self, session_id):
        return self.generate_recommendations(session_id)