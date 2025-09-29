from pydantic import BaseModel, Field

class CSQuestion(BaseModel):
    questions_type: list[str] = Field(..., description="List of question types for each question, should be 'os', 'dbms', 'oops', 'cn'")
    questions: list[str] = Field(..., description="List of CS interview questions")
    answers: list[str] = Field(..., description="List of expected answers or answer expectations for each question")