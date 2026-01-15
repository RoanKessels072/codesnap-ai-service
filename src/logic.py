import re
import os
from typing import Optional
from google import genai
from src.config import settings

client = None

def get_client():
    global client
    if not client:
        client = genai.Client(api_key=settings.google_api_key)
    return client

def extract_code_from_markdown(text: str, language: str = None) -> str:
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
            model="models/gemini-2.5-flash",
            contents=[prompt]
        )
        text = response.text.strip()
        text = re.sub(r'^```[a-zA-Z]*\n', '', text)
        text = re.sub(r'\n```$', '', text)
        return text
    except Exception as e:
        print(f"GenAI Error (Feedback): {e}")
        return f"# Error generating feedback: {str(e)}"

def generate_rival_logic(language: str, exercise_name: str, description: str, difficulty: str, starter_code: Optional[str], function_name: str) -> str:
    client = get_client()
    
    code_context = ""
    if starter_code:
        code_context = f"Starter code:\n{starter_code}"
    else:
        code_context = f"Function Signature required: function named '{function_name}'."

    prompt = f"""
        You are an AI competitor in a coding exercise. Create a solution in {language}.

        Instructions:
        - Your goal is to provide a plausible solution to the exercise.
        - You MUST use the exact function signature/name provided in the starter code below.
        - Complete the function implementation based on the exercise description.
        - **CRITICAL**: If the exercise requires returning specific strings (like "Hello, World!"), you MUST respect punctuation (commas, exclamation marks) EXACTLY as described.
        - Difficulty Adjustments:
          - **easy**: Introduce syntax errors or major logic flaws (e.g., return incorrect type, infinite loop possibility).
          - **medium**: Implement a naive solution that works for basic cases but fails edge cases or uses inefficient logic (O(n^2) instead of O(n)).
          - **hard**: Provide an almost optimal, production-ready solution. It should pass all tests including edge cases, but have minor style issues to still remain beatable.
        - Output ONLY the executable code with NO explanations, NO markdown, NO additional text.
        - Do NOT use markdown code blocks (```). 
        - Start immediately with the function definition.

        Context:
        Exercise name: {exercise_name}
        Exercise description: {description}
        Difficulty: {difficulty}
        
        {code_context}
    """
    
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[prompt]
        )
        text = response.text.strip()
        text = extract_code_from_markdown(text, language)
        return text
    except Exception as e:
        print(f"GenAI Error (Rival): {e}")
        return starter_code if starter_code else f"def {function_name}():\n    pass"