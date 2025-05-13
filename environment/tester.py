"""
Code testing and evaluation utilities.
"""

import re
import subprocess
import logging
from config import TEMPFILE_LOCATION


def test_code(code, problem):
  """
    Test the generated code for validity.
    
    Args:
      code (str): The generated code.
      problem (dict): The problem dictionary.
        
    Returns:
      str: A string containing the error message, or None if successful.
    """
  # Create a temporary file to test the code
  with open(TEMPFILE_LOCATION, "w") as f:
    f.write(code)
    f.write("\n\n")
    for assert_statement in problem.get("test_list", []):
      line = re.sub(
        r'assert\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', 'assert candidate(', assert_statement
      )
      f.write(f"{line}\n")

  # Run the code using subprocess & docker
  container_name = f"sandbox-test-{hash(code)[:8]}" if len(
    code
  ) > 8 else f"sandbox-test-{hash(code)}"

  try:
    output = subprocess.run([
      "docker", "compose", "run", "--rm", "--name", container_name, "--no-TTY",
      "sandbox", "python3", TEMPFILE_LOCATION
    ],
                            check=True,
                            capture_output=True,
                            text=True,
                            timeout=15)
    logging.info(f"Code executed successfully.")
    return None
  except subprocess.TimeoutExpired as e:
    logging.warning(f"Code execution timed out after {e.timeout} seconds.")
    return f"Execution timed out after {e.timeout} seconds. The code may contain an infinite loop or faulty recursion."
  except FileNotFoundError as e:
    # If the file is not found, log the error
    logging.error(f"File not found: {e}")
    return str(e)
  except subprocess.CalledProcessError as e:
    # If the code fails, capture the error message
    if e.returncode != 0:
      return e.stderr
    else:
      logging.error(f"Error running code: {e}")
      return e.stderr
  except Exception as e:
    logging.error(f"Unexpected error: {e}")
    return f"Unexpected error: {e}"

  finally:
    try:
      # Force stop the container if it's still running
      subprocess.run(
        ["docker", "stop", container_name],
        check=False,  # Don't fail if container is already stopped
        capture_output=True,
        timeout=5
      )

      # Remove the container even if it failed to stop normally
      subprocess.run(
        ["docker", "rm", "-f", container_name],
        check=False,  # Don't fail if container doesn't exist
        capture_output=True,
        timeout=5
      )
    except Exception as cleanup_error:
      logging.warning(f"Error cleaning up: {cleanup_error}")
