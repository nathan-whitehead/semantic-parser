"""
Code generation using local Ollama API.
"""

import re
import requests
import logging
from config import DEFAULT_PROMPT, CORRECTION_PROMPT, MODEL, OLLAMA_API_URL
from problem_loader import get_problem_description


def get_code_prompt(problem):
  """
    Create a prompt for the code generation model.
    The prompt includes the problem description and the default prompt.
    
    Args:
        problem (dict): Problem dictionary.
        
    Returns:
        str: Complete prompt for code generation.
    """
  problem_description = get_problem_description(problem)
  return f"{DEFAULT_PROMPT}\n\n{problem_description}\n\n"


def generate_code_with_ollama(prompt, model=MODEL, temperature=0.4, timeout=60):
  """
    Generate code using Ollama API.
    
    Args:
        prompt (str): The prompt to send to Ollama.
        model (str): The model to use.
        temperature (float): Controls randomness (0.0-1.0).
        timeout (int): Maximum time in seconds to wait for a response.
        
    Returns:
        str: Generated code or None if an error occurred.
    """
  payload = {
    "model": model,
    "prompt": prompt,
    "stream": False,
    "temperature": temperature
  }

  try:
    response = requests.post(OLLAMA_API_URL, json=payload, timeout=timeout)
    response.raise_for_status()  # Raise an exception for HTTP errors

    result = response.json()
    return result["response"]
  except requests.exceptions.Timeout:
    logging.error(f"Request timed out after {timeout} seconds")
    return None
  except requests.exceptions.RequestException as e:
    logging.error(f"Error calling Ollama API: {e}")
    return None


def extract_code_and_explanation(response):
  """
    Extract code and explanation from the response.
    
    Args:
        response (str): The response string from the model.
        
    Returns:
        tuple: A tuple containing the code and explanation.
    """
  # Use regex to extract the code block and explanation
  match = re.search(r"(?s)(.*?)(```python\n(.*?)\n```)", response)
  if match:
    explanation = match.group(1).strip()
    code = match.group(3).strip()
    return code, explanation
  else:
    match = re.search(r"(?s)(.*?)(```(?:python)?\n(.*?)\nEOF\n)", response + "\nEOF\n")
    if match:
      explanation = match.group(1).strip()
      code = match.group(3).strip()
      return code, explanation
    else:
      # If no match is found, return None for both
      logging.error(f"Failed code extraction. Response:\n\n{response}")
  return None, None


def solve_problem_with_ollama(problem, model=MODEL):
  """
    Generate code for a given problem using Ollama.
    
    Args:
        problem (dict): Problem dictionary with text description.
        model (str): Ollama model to use.
        
    Returns:
        str: Generated code solution.
    """
  prompt = get_code_prompt(problem)
  solution = generate_code_with_ollama(prompt, model)
  if solution is None:
    logging.error("Failed to generate code.")
    return None, None
  # Extract code block from the response
  code, explanation = extract_code_and_explanation(solution)
  if code is None:
    logging.error(f"Failed to extract code from the response \n\n{solution}")
    return None, None
  # Return the code block
  return code, explanation


def correct_code(code, problem, error_msg):
  """
    Correct the generated code using the model.
    
    Args:
        code (str): The generated code.
        problem (dict): The problem dictionary.
        error_msg (str): The error message from the test.
        
    Returns:
        str: The corrected code.
    """
  prompt = get_problem_description(problem)
  if not code or not error_msg:
    logging.error("Invalid code or error message.")
    return solve_problem_with_ollama(problem)
  corrected_prompt = CORRECTION_PROMPT.replace("%%%PROMPT%%%", prompt) \
                                    .replace("%%%CODE%%%", code) \
                                    .replace("%%%ERROR%%%", error_msg)

  solution = generate_code_with_ollama(corrected_prompt)
  if solution is None:
    logging.error("Failed to generate code.")
    return None, None
  # Extract code block from the response
  corrected_code, explanation = extract_code_and_explanation(solution)
  if corrected_code is None:
    logging.error("Failed to extract code from the response.")
    return None, None
  # Return the code block
  return corrected_code, explanation
