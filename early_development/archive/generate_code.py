import subprocess, json, os, sys, shutil, re, requests
from pathlib import Path

import logging

logging.basicConfig(
  level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

PROBLEM_SET_LOCATION = "/Users/nathanjay/Documents/University Documents/2025 1 Spring/CS6375 Machine Learning/project/semantic-parser/early_development/problems.jsonl"

DEFAULT_PROMPT = """
You are a python expert. You will be given a prompt to create a python funcion.
Your task is to create a python function that solves the problem described in the prompt.

**IMPORTANT**
- Your response must be ONLY valid JSON with no additional text, markdown formatting, backticks, or explanations before or after the JSON. Do not wrap your response in ```json or ``` markers.
- The JSON object should start with {{ and end with }} with nothing else before or after.
- The JSON object should contain the following fields in this order:
  - `explanation`: a short explanation of the code and your approach.
  - `code`: the code of the function.
- In valid JSON, both keys and values should be in double quotes. (e.g., "key": "value").


**EXPLANATION RULES**
- The explanation should be no more than 3 sentences.
- The explanation should be in plain text with no formatting.
- The explanation should describe the code, the approach, and any important details.

**CODE RULES**
- The function should be a valid python function.
- The function should be named `candidate`.
- The function should not contain any print statements.
- The function should contain explanatory comments.
- Only output a single function. If you are unsure, output the most universal version of the function.
- If subfunctions are needed, they should be defined inside the main function.
- The `code` block in the JSON object should include newlines and indentation.
"""

HOSTNAME = "localhost"
PORT = 11434
OLLAMA_API_URL = f"http://{HOSTNAME}:{PORT}/api/generate"
MODEL = "llama3.2:1b"
MAX_ITER = 5

# -----


def load_problem_set():
  """
  Load the problem set from the JSONL file.
  Each line in the file is a separate JSON object.
  """
  problems = []
  with open(PROBLEM_SET_LOCATION, "r") as f:
    for line in f:
      if line.strip():  # Skip empty lines
        problems.append(json.loads(line))
  return problems


def get_problem_description(problem):
  """
  Get the problem description from the problem dictionary.
  The description is in the 'text' field.
  """
  return problem.get("text", "")


def get_code_prompt(problem):
  """
  Create a prompt for the code generation model.
  The prompt includes the problem description and the default prompt.
  """
  problem_description = get_problem_description(problem)
  return f"{DEFAULT_PROMPT}\n\n{problem_description}\n\n"


def generate_code_with_ollama(prompt, model=MODEL, temperature=0.7):
  """
    Generate code using Ollama API
    
    Args:
        prompt (str): The prompt to send to Ollama
        model (str): The model to use (default: llama3)
        temperature (float): Controls randomness (0.0-1.0)
        
    Returns:
        str: Generated code
    """
  url = OLLAMA_API_URL

  payload = {
    "model": model,
    "prompt": prompt,
    "stream": False,
    "temperature": temperature
  }

  try:
    response = requests.post(url, json=payload)
    response.raise_for_status()  # Raise an exception for HTTP errors

    result = response.json()
    return result["response"]
  except requests.exceptions.RequestException as e:
    print(f"Error calling Ollama API: {e}")
    return None


def solve_problem_with_ollama(problem, model=MODEL):
  """
    Generate code for a given problem using Ollama
    
    Args:
        problem (dict): Problem dictionary with text description
        model (str): Ollama model to use
        
    Returns:
        str: Generated code solution
    """
  prompt = get_code_prompt(problem)
  solution = generate_code_with_ollama(prompt, model)
  return solution


def extract_json_from_response(response):
  """
  Extract JSON from the response string.
  
  Args:
    response (str): The response string from the model.
      
  Returns:
    dict: The extracted JSON object.
  """
  if not response:
    return None

  # Try to find JSON content between curly braces
  json_match = re.search(r'(\{.*\})', response, re.DOTALL)
  if json_match:
    json_str = json_match.group(1)
    try:
      return json.loads(json_str)
    except json.JSONDecodeError:
      pass

  # If no valid JSON found with regex, try other approaches
  try:
    # Remove code block markers if present
    cleaned = re.sub(r'```json|```', '', response).strip()
    return json.loads(cleaned)
  except json.JSONDecodeError:
    logging.error("Could not extract valid JSON from response")
    return None


def solve_problem(problem):
  """
  Solve a problem iteratively using the Ollama model.
  
  Args:
    problem (dict): The problem dictionary.
    
  Returns:
    dict: The solution containing explanation and code.
  """

  for i in range(MAX_ITER):
    # Generate code using the model
    response = solve_problem_with_ollama(problem)

    # Extract JSON from the response
    json_response = extract_json_from_response(response)

    if json_response:
      # Check if the response contains valid JSON
      if "code" in json_response and "explanation" in json_response:
        return json_response

    # later, add tests for correctness.

    # If the response is not valid, log the error and try again
    logging.error(f"Iteration {i + 1}: Invalid response, retrying...")


# -----


def main():
  # main
  problems = load_problem_set()

  sample_problems = problems[:1]

  for problem in sample_problems:
    solution = solve_problem(problem)
    print(solution)
    print("\n\n\n")


if __name__ == "__main__":
  main()
