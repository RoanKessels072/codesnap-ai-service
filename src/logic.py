import re
import os
from google import genai
from src.config import settings

client = None

def get_client():
    global client
    if not client:
        client = genai.Client(api_key=settings.google_api_key)
    return client

def extract_code_from_markdown(text: str, language: str = None) -> str:
    """Extract code from markdown code blocks."""
    pattern = r'```(?:' + (language or r'\w*') + r')?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return matches[0].strip()
    return text.strip()

def generate_feedback_logic(code: str, language: str, exercise_name: str, description: str, reference_solution: str) -> str:
    client = get_client()
    prompt = f"""
        You are a coding assistant. The user is working on a coding exercise.

        Instructions:
        - Review the provided code and the exercise reference solution.
        - Suggest **ONLY ONE NEXT STEP or hint** that helps the user progress toward the reference solution.
        - Also provide **feedback on likely errors, edge-cases, or bad practices** (max 3 bullets).
        - Output everything as **inline code comments** appropriate for {language}.
        - Do NOT rewrite or delete user code. Do NOT provide full solutions.
        - Be concise: next step on the first line, then a blank line, then the bullet list.

        Context:
        Exercise name: {exercise_name}
        Exercise description: {description}
        Reference solution: {reference_solution}
        User code:
        {code}
    """
    
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-pro",
            contents=[prompt]
        )
        text = response.text.strip()
        text = re.sub(r'^```[a-zA-Z]*\n', '', text)
        text = re.sub(r'\n```$', '', text)
        return text
    except Exception as e:
        print(f"GenAI Error (Feedback): {e}")
        return f"# Error generating feedback: {str(e)}"

def generate_rival_logic(language: str, exercise_name: str, description: str, difficulty: str, starter_code: str) -> str:
    client = get_client()
    prompt = f"""
        You are an AI competitor in a coding exercise. Create a solution in {language}.

        Instructions:
        - Your goal is to provide a plausible solution to the exercise.
        - You MUST use the exact function signature/name provided in the starter code below.
        - Complete the function implementation based on the exercise description.
        - Depending on the difficulty level, introduce mistakes, inefficiencies, or edge-case oversights:
          - easy → more likely to have obvious mistakes (wrong logic, missing return, etc.)
          - medium → subtle mistakes or missing edge cases
          - hard → mostly correct, small inefficiencies or minor mistakes
        - Output ONLY the executable code with NO explanations, NO markdown, NO additional text.
        - Do NOT use markdown code blocks (```). 
        - Start immediately with the function definition.

        Context:
        Exercise name: {exercise_name}
        Exercise description: {description}
        Difficulty: {difficulty}
        
        Starter code:
        {starter_code}
    """
    
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-pro",
            contents=[prompt]
        )
        text = response.text.strip()
        text = extract_code_from_markdown(text, language)
        return text
    except Exception as e:
        print(f"GenAI Error (Rival): {e}")
        return starter_code