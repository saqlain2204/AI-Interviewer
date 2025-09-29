
def generate_core_cs_introduction_prompt(company_name: str, role: str) -> str:
    INTRO_PROMPT = (
        f"Hello! My name is Algo, and I am a Senior Software Engineer at {company_name}. "
        f"I have been working here for 4 years, leading and mentoring engineering teams. "
        f"I'm excited to learn more about you. "
        f"Could you please start by giving me a brief introduction about yourself?"
    )
    return INTRO_PROMPT

def generate_core_cs_questions_prompt(experience_level: str, role: str, company_name: str, about_company: str) -> str:
    prompt = f"""
    You are a technical interviewer at {company_name}. The candidate is applying for the role of {role} with experience level: {experience_level}.
    Here is some information about the company: {about_company}
    
    There must be a total of 10 questions covering the following core computer science topics: Operating Systems (os), Database Management Systems (dbms), Object-Oriented Programming (oops), and Computer Networks (cn).
    Based on the company and what they do, manage the distribution of questions across these topics accordingly.

    Generate a JSON object in the following format:
    {{
    question_types: [list of question types for each question] (should be 'os', 'dbms', 'oops', 'cn'),
    questions: [list of 10 core computer science interview questions tailored to the role, company_name, experience level, and about the company],
    answers: [list of 10 expected answers or answer expectations for each question. The expected answers must be specific and in detail]
    }}

    Only return the JSON object, nothing else.
    """
    return prompt