"""
Utility functions for the code generation environment.
"""

import logging
import json


def setup_logging():
  """Configure logging for the application."""
  logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
  )


def save_response(response, filename):
  """
  Save the response to a file as JSON.
  
  Args:
      response (dict): The response dictionary to save.
      filename (str): The name of the file to save the response to.
  """
  with open(filename, 'w') as f:
    json.dump(response, f, indent=2)
  logging.info(f"Response saved to {filename}")
