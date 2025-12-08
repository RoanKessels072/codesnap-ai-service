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
    starter_code: Optional[str] = None
    function_name: str
    test_cases: list

class RivalResponse(BaseModel):
    ai_code: str
    score: int
    stars: int
    tests_passed: int
    tests_total: int
    ai_result: dict[str, Any]