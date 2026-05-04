import os
import random
import datetime
import re
from google import genai
from dotenv import load_dotenv
import ollama # New import for Ollama

load_dotenv()

# Client and Model initialization for Gemini
client = genai.Client(api_key=os.getenv("API_KEY"))
GEMINI_MODEL_ID = "gemini-2.5-flash" # Renamed for clarity

# Ollama Model Initialization
OLLAMA_MODEL_ID = "llama3.2:1b" # Using 'llama3.1' as a common variant for 'llama3,2:1b'
                             # User might need to pull this model first: ollama pull llama3.1

OPERATIONS = {
    "add": (["add", "sum", "+"], lambda x, y: x + y, "sum"),
    "sub": (["subtract", "minus", "-"], lambda x, y: x - y, "difference"),
    "mul": (["multiply", "*", "x"], lambda x, y: x * y, "product"),
    "div": (["divide", "/"], lambda x, y: x / y if y != 0 else "Error: Division by zero", "quotient"),
}

def get_numbers(text, count=2):
    nums = [float(s) for s in re.findall(r'-?\d+\.?\d*', text)]
    return nums[:count]

def handle_gemini(prompt):
    try:
        # Updated method call for the new SDK
        response = client.models.generate_content(
            model=GEMINI_MODEL_ID, # Use GEMINI_MODEL_ID
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error connecting to Gemini: {e}"

# New function for Ollama
def handle_ollama(prompt, model_id=OLLAMA_MODEL_ID):
    try:
        response = ollama.generate(model=model_id, prompt=prompt)
        return response['response']
    except Exception as e:
        return f"Error connecting to Ollama: {e}. Make sure Ollama server is running and model '{model_id}' is pulled."

def process_request(prompt, llm_provider="gemini"): # Added llm_provider argument
    prompt_lower = prompt.lower()

    # Math Check
    for key, (keywords, func, label) in OPERATIONS.items():
        if any(word in prompt_lower for word in keywords):
            nums = get_numbers(prompt_lower)
            if len(nums) >= 2:
                return f"The {label} is: {func(nums[0], nums[1])}"

    # Utility Checks
    if any(w in prompt_lower for w in ["toss", "flip"]):
        result = random.choice(["heads", "tails"])
        return f"The coin landed on: {result.upper()}!"

    if any(w in prompt_lower for w in ["date", "time", "now"]):
        return f"Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Fallback to chosen LLM
    if llm_provider == "ollama":
        return handle_gemini(prompt)
    elif llm_provider == "gemini":
        return handle_ollama(prompt)
    else:
        return "Invalid LLM provider specified. Choose 'gemini' or 'ollama'."