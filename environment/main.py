"""
Main program for code generation using LLMs.
"""

import logging, os
from utils import setup_logging, save_response
from config import MAX_ITER, MODEL
from problem_loader import load_problem_set
from generator import solve_problem_with_ollama, extract_code_and_explanation, correct_code
from tester import test_code


def solve_problem(problem):
  """
    Solve a problem iteratively using the LLM.
    
    Args:
        problem (dict): The problem dictionary.
        
    Returns:
        dict: A dictionary containing the task ID, generated code, explanation,
              number of iterations, error message, and status.
    """
  logging.info(f"Solving problem: {problem['task_id']}")

  return_object = {
    "task_id": problem["task_id"],
    "code": None,
    "explanation": None,
    "num_iterations": 0,
    "error_msg": None,
    "success": None
  }

  # Generate code using the LLM
  code, explanation = solve_problem_with_ollama(problem)
  return_object["num_iterations"] += 1
  if code is None:
    logging.error("  Failed to extract code from the response.")
    return solve_problem(problem)

  # Test the code for validity
  logging.info("  Testing generated code")
  error_msg = test_code(code, problem)
  if not error_msg or error_msg == "":
    return_object["code"] = code
    return_object["explanation"] = explanation
    return_object["success"] = True

    logging.info(f"  Code executed successfully.")
    # If the code is valid, return the explanation and code
    return return_object

  # If the code is not valid, log the error and retry

  for i in range(MAX_ITER):
    logging.info(f"  Invalid response, retrying iteration {i + 1} of {MAX_ITER}")

    # Correct the code using the model
    code, explanation = correct_code(code, problem, error_msg)
    return_object["num_iterations"] += 1

    if code is None:
      logging.error("  Failed to extract code from the response.")
      continue

    error_msg = test_code(code, problem)
    if not error_msg or error_msg == "":
      return_object["code"] = code
      return_object["explanation"] = explanation
      return_object["success"] = True
      # If the code is valid, return the explanation and code
      logging.info(f"  Code executed successfully.")
      return return_object

    # If the response is not valid, log the error and try again

  logging.error("  Max iterations reached, returning last code.")
  return_object["code"] = code
  return_object["explanation"] = explanation
  return_object["error_msg"] = error_msg
  return_object["success"] = False
  return return_object


def main():
  """Main entry point for the program."""
  setup_logging()

  logging.info("Loading problem set")
  problems = load_problem_set()

  # For development
  # problems = problems[70]

  logging.info(f"Generating code for {len(problems)} problems")
  for problem in problems:
    res = solve_problem(problem)

    if res:
      os.makedirs(f"output-{MODEL.replace(':','')}", exist_ok=True)
      save_response(
        res, f"output-{MODEL.replace(':','')}/response_{problem['task_id']}.json"
      )
      logging.info(f"Problem solved: {problem['task_id']}")
    else:
      logging.error(f"Failed to solve problem: {problem['task_id']}")
      continue


if __name__ == "__main__":
  main()
