from pydantic import BaseModel, Field
from typing import Literal

class UserPreferences(BaseModel):
    company_name: str
    role: str
    experience_level: Literal['fresher', 'experienced']
    company_website: str
    type_of_interview: Literal['hr', 'core_cs']
    
    