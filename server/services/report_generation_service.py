import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from pathlib import Path
from services.llm_utils import get_llm_insight, get_llm_summary

def generate_report(log_data, output_path):
    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    left_margin = 60
    indent1 = left_margin + 30
    indent2 = left_margin + 60
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left_margin, y, "AI Interview Report")
    y -= 36
    c.setFont("Helvetica", 12)
    c.drawString(left_margin, y, f"User Introduction: {log_data['user_intro']}")
    y -= 36
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left_margin, y, "Question-by-Question Analysis:")
    y -= 26
    c.setFont("Helvetica", 11)
    for idx, q in enumerate(log_data["questions"], 1):
        if y < 100:
            c.showPage()
            y = height - 50
        # Question (blue)
        c.setFillColorRGB(0.18, 0.36, 0.8)  # blue
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left_margin, y, f"Q{idx}: {q.get('question', '')}")
        y -= 18
        # Expected answer (green, indented)
        expected = q.get('expected_answer', 'N/A')
        c.setFillColorRGB(0.18, 0.6, 0.36)  # green
        c.setFont("Helvetica", 11)
        c.drawString(indent1, y, f"Expected: {expected}")
        y -= 16
        # User answer (purple, indented)
        user_ans = q.get('user_answer', '')
        c.setFillColorRGB(0.4, 0.2, 0.6)  # purple
        c.drawString(indent1, y, f"User: {user_ans}")
        y -= 16
        # LLM insight (gray, more indented)
        insight = get_llm_insight_temp(q.get('question', ''), expected, user_ans)
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColorRGB(0.3, 0.3, 0.3)  # gray
        c.drawString(indent2, y, f"Insight: {insight}")
        c.setFont("Helvetica", 11)
        y -= 28
        c.setFillColorRGB(0, 0, 0)  # reset to black
    # Compiled summary
    summary = get_llm_summary_temp(log_data)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left_margin, y, "Overall Interview Summary:")
    y -= 22
    c.setFont("Helvetica", 11)
    for line in summary.split('\n'):
        if y < 60:
            c.showPage()
            y = height - 50
        c.drawString(indent1, y, line)
        y -= 16
    c.save()

# Example LLM utility functions (to be implemented with your LLM API)
def get_llm_insight_temp(question, expected, user):
    return get_llm_insight(question, expected, user)

def get_llm_summary_temp(log_data):
    
    return get_llm_summary(log_data)
