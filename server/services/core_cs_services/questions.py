from llm import get_text_model
from services.core_cs_services.models import CSQuestion
from services.core_cs_services.prompts import generate_core_cs_questions_prompt
from services.web_scraping import scrape_website

def generate_core_cs_questions(experience_level, role, company_name, company_website) -> CSQuestion:
    model = get_text_model()
    about_company = scrape_website(company_website)
    response = model.with_structured_output(CSQuestion).invoke(generate_core_cs_questions_prompt(experience_level, role, company_name, about_company))
    return response


    
    