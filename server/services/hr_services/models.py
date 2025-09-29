from pydantic import BaseModel, Field

class HRQuestions(BaseModel):
    questions_type: list[str] = Field(..., description="List of question types for each question, should be 'hr'")
    questions: list[str] = Field(..., description="List of HR interview questions")
    answers: list[str] = Field(..., description="List of expected answers or answer expectations for each question")