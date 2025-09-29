from llm import get_text_model
from services.hr_services.prompts import generate_hr_introduction_prompt, generate_hr_questions_prompt
from services.hr_services.models import HRQuestions
from services.web_scraping import scrape_website

def generate_hr_questions(experience_level, role, company_name, company_website) -> HRQuestions:
    model = get_text_model()
    about_company = scrape_website(company_website)
    response = model.with_structured_output(HRQuestions).invoke(generate_hr_questions_prompt(experience_level, role, company_name, about_company))
    return response


    
    