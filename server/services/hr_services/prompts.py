def generate_hr_introduction_prompt(company_name: str, role: str) -> str:
    HR_INTRO_PROMPT = (
        f"Hello! My name is Algo, and I am the HR representative at {company_name}. "
        f"I have been working here for 4 years, and I manage the HR operations and talent acquisition for the company. "
        f"Could you please start by giving me a brief introduction about yourself?"
    )
    return HR_INTRO_PROMPT

def generate_hr_questions_prompt(experience_level: str, role: str, company_name: str, about_company: str) -> str:
    prompt = f"""
    You are an HR interviewer at {company_name}. The candidate is applying for the role of {role} with experience level: {experience_level}.
    Here is some information about the company: {about_company}

    Generate a JSON object in the following format:
    {{
    questions_type: [list of question types] (all should be 'hr'),
    questions: [list of 10 HR interview questions tailored to the role, company_name, experience level, and about the company],
    answers: [list of 10 expected answers or answer expectations for each question. The expected answers must be specific and in detail]
    }}

    Only return the JSON object, nothing else.
    """
    return prompt
