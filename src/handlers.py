from src.schemas import AssistantFeedbackRequest, RivalGenerationRequest, RivalResponse, AssistantFeedbackResponse
from src.logic import generate_feedback_logic, generate_rival_logic
from src.nats_client import NATSClient

nats_client_instance: NATSClient = None

def set_nats_client(client: NATSClient):
    global nats_client_instance
    nats_client_instance = client

async def handle_get_feedback(data: dict):
    msg = AssistantFeedbackRequest(**data)
    
    feedback = generate_feedback_logic(
        code=msg.code,
        language=msg.language,
        exercise_name=msg.exercise_name,
        description=msg.exercise_description,
        reference_solution=msg.reference_solution
    )
    
    return AssistantFeedbackResponse(response=feedback).model_dump(mode='json')

async def handle_generate_rival(data: dict):
    msg = RivalGenerationRequest(**data)
    
    ai_code = generate_rival_logic(
        language=msg.language,
        exercise_name=msg.exercise_name,
        description=msg.exercise_description,
        difficulty=msg.difficulty,
        starter_code=msg.starter_code,
        
    )
    
    try:
        grading_payload = {
            "exercise_id": msg.exercise_id,
            "code": ai_code,
            "language": msg.language,
            "function_name": msg.function_name,
            "test_cases": msg.test_cases
        }
        
        grading_result = await nats_client_instance.request(
            "attempts.grade_ephemeral", 
            grading_payload, 
            timeout=20.0
        )
    except Exception as e:
        print(f"Error requesting grading for AI rival: {e}")
        grading_result = {
            "score": 0, 
            "stars": 0, 
            "tests_passed": 0, 
            "tests_total": 0,
            "error": "Could not grade AI code"
        }

    return RivalResponse(
        ai_code=ai_code,
        ai_result=grading_result
    ).model_dump(mode='json')