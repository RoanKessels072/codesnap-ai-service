from pydantic import BaseModel
from typing import Optional, Any

class AssistantFeedbackRequest(BaseModel):
    code: str
    language: str
    exercise_name: str
    exercise_description: str
    reference_solution: Optional[str] = ""

class AssistantFeedbackResponse(BaseModel):
    response: str

class RivalGenerationRequest(BaseModel):
    exercise_id: int
    exercise_name: str
    exercise_description: str
    difficulty: str = "easy"
    language: str
    starter_code: str
    function_name: str
    test_cases: list

class RivalResponse(BaseModel):
    ai_code: str
    ai_result: dict[str, Any]