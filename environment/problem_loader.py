"""
Problem loading and management utilities.
"""

import json
from config import PROBLEM_SET_LOCATION


def load_problem_set():
  """
    Load the problem set from the JSONL file.
    Each line in the file is a separate JSON object.
    
    Returns:
        list: List of problem dictionaries.
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
    
    Args:
        problem (dict): Problem dictionary.
        
    Returns:
        str: The problem description text.
    """
  return problem.get("text", "")
