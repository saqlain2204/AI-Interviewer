from llm import get_text_model  # Import the function to get a new LLM instance

# Helper to get a response from the LLM
def llm(prompt):
    model = get_text_model()
    response = model.invoke(prompt)
    return response.content if hasattr(response, 'content') else str(response)

def get_llm_insight(question, expected, user):
    prompt = f"""
    Analyze the following interview question and answer:
    Question: {question}
    Expected Answer: {expected}
    User Answer: {user}
    Metrics: Clarity of thought, complexity, ease of understanding.
    Provide a short analysis and suggestions for improvement.
    """
    response = llm(prompt)
    return response.strip() if response else "No insight generated."

def get_llm_summary(log_data):
    import json
    prompt = f"""
    Interview log:
    User Intro: {log_data['user_intro']}
    Questions: {json.dumps(log_data['questions'], indent=2)}
    Provide an overall summary, strengths, weaknesses, and actionable feedback.
    """
    response = llm(prompt)
    return response.strip() if response else "No summary generated."
