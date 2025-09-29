import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
from services.llm_utils import get_llm_insight, get_llm_summary

def generate_report(log_data, output_path):
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    y = height - 40
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "AI Interview Report")
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(40, y, f"User Introduction: {log_data['user_intro']}")
    y -= 30
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Question-by-Question Analysis:")
    y -= 20
    c.setFont("Helvetica", 11)
    for idx, q in enumerate(log_data["questions"], 1):
        if y < 100:
            c.showPage()
            y = height - 40
        # Question (blue)
        c.setFillColorRGB(0.18, 0.36, 0.8)  # blue
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"Q{idx}: {q.get('question', '')}")
        y -= 16
        # (question_type removed)
        # Expected answer (green)
        expected = q.get('expected_answer', 'N/A')
        c.setFillColorRGB(0.18, 0.6, 0.36)  # green
        c.drawString(60, y, f"Expected: {expected}")
        y -= 14
        # User answer (purple)
        user_ans = q.get('user_answer', '')
        c.setFillColorRGB(0.4, 0.2, 0.6)  # purple
        c.drawString(60, y, f"User: {user_ans}")
        y -= 14
        # LLM insight (gray)
        insight = get_llm_insight_temp(q.get('question', ''), expected, user_ans)
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColorRGB(0.3, 0.3, 0.3)  # gray
        c.drawString(60, y, f"Insight: {insight}")
        c.setFont("Helvetica", 11)
        y -= 22
        c.setFillColorRGB(0, 0, 0)  # reset to black
    # Compiled summary
    summary = get_llm_summary_temp(log_data)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Overall Interview Summary:")
    y -= 18
    c.setFont("Helvetica", 11)
    for line in summary.split('\n'):
        if y < 60:
            c.showPage()
            y = height - 40
        c.drawString(50, y, line)
        y -= 14
    c.save()

# Example LLM utility functions (to be implemented with your LLM API)
def get_llm_insight_temp(question, expected, user):
    return get_llm_insight(question, expected, user)

def get_llm_summary_temp(log_data):
    
    return get_llm_summary(log_data)
