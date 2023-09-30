from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)
openai.api_key = "API-KEY"


# List to store feedbacks
feedbacks = []
Question= "What do you believe we could change or implement to make our company more effective and enhance your experience working here?"

message = {
    "role": "system",
    "content": "You are expert in translating feedback into actionable insight and a helpful assistant."
}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze_feedback', methods=['POST'])
def analyze_feedback():
    feedback = request.form.get('feedback')
    feedbacks = [] # make sure the feedback is empthy list
    feedbacks.append(feedback)

    user_message = {
        "role": "user",
        "content": f"Keep it short, and do not make up if no obvious insight. As a member of higher management, analyze the following feedback based on this question {Question} and provide actionable insights if exist for this feedback: \n{feedback}"
    }
    
    insights_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[message, user_message]
    )

    insights = insights_response['choices'][0]['message']['content']

    user_message = {
        "role": "user",
        "content": f"Keep it short, ask the feedback provider back to determine if the following insights are actionable. If not, generate a clarifying question:\n{insights}\nClarifying Question:"
    }

    clarifying_question_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[message, user_message]
    )

    clarifying_question = clarifying_question_response['choices'][0]['message']['content']

    return jsonify({'insights': insights, 'clarifying_question': clarifying_question})

@app.route('/refine_insights', methods=['POST'])
def refine_insights():
    original_feedback = request.form.get('original_feedback')
    clarifying_answer = request.form.get('clarifying_answer')
    feedbacks.append(clarifying_answer)

    user_message = {
        "role": "user",
        "content": f"Keep it short, but effective, as a member of higher management at Mercedes Benz, refine the actionable insights based on the original feedback  based on this question {Question} and clarifying answer:\nOriginal Feedback: {original_feedback}\nClarifying Answer: {clarifying_answer}\nRefined Insights:"
    }

    refined_insight_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[message, user_message]
    )

    refined_insight = refined_insight_response['choices'][0]['message']['content']
    return jsonify({'refined_insight': refined_insight})

@app.route('/get_feedback_summary', methods=['GET'])
def get_feedback_summary():
    combined_feedbacks = ' '.join(feedbacks)

    user_message = {
        "role": "user",
        "content": f"given this {Question}, Provide a concise summary without providing more information of the following feedbacks:\n{combined_feedbacks}\nSummary:"
    }

    summary_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[message, user_message]
    )

    summary = summary_response['choices'][0]['message']['content']
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)
