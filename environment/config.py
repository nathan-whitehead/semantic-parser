"""
Configuration settings for the code generation environment.
"""

# file paths
PROBLEM_SET_LOCATION = "problems.jsonl"
DOCKER_SANDBOX_LOCATION = "sandbox"
TEMPFILE_LOCATION = DOCKER_SANDBOX_LOCATION + "/temp_code.py"

# llm settings
PROGRAMMING_LANGUAGE = "python"
HOSTNAME = "localhost"
PORT = 11434
OLLAMA_API_URL = f"http://{HOSTNAME}:{PORT}/api/generate"
MODEL = "llama3.2:latest"
MAX_ITER = 5

DEFAULT_PROMPT = f"""
You are a {PROGRAMMING_LANGUAGE} expert. You will be given a prompt to create a {PROGRAMMING_LANGUAGE} funcion.
Your task is to create a {PROGRAMMING_LANGUAGE} function that solves the problem described in the prompt.
Create the simplest function that solves the problem.

**IMPORTANT**
- The response should be in markdown format, with the code block labeled as '{PROGRAMMING_LANGUAGE}'.
- The response should contain two parts: explanation and code, in that order.
- Example: Explanation sentences.\n```{PROGRAMMING_LANGUAGE}\n# code here\n```
- There should only be ONE explanation section, and ONE code block in the response.
- No other text should be included in the response.

**EXPLANATION RULES**
- The explanation should be no more than 3 sentences.
- The explanation should describe the code, the approach, and any important details.

**CODE RULES**
- The function should be a valid {PROGRAMMING_LANGUAGE} function.
- The function should be named `candidate`.
- The function should not contain any print statements.
- The function should contain explanatory comments.
- Only output a single function. If you are unsure, output the most universal version of the function.
- If subfunctions are needed, they should be defined inside the main function.
- No code should be outside the function.
- No test cases should be included in the code block.
"""
CORRECTION_PROMPT = f"""
You are a {PROGRAMMING_LANGUAGE} expert. You help to correct user-generated code and fix errors or failed tests.
The code below is not valid. You will be given:
- the original prompt for the code
- the code that was generated
- the error message from the test

Your task is to correct the code and make it valid and pass the test. 
The user code is not necessarily well-structured, so you should feel 
free to rewrite, refactor, and improve the code as needed.

The following rules must apply to your response:

**IMPORTANT**
- The response should be in markdown format, with the code block labeled as '{PROGRAMMING_LANGUAGE}'.
- The response should contain two parts: explanation and code, in that order.
- Example: Explanation sentences.\n```{PROGRAMMING_LANGUAGE}\n# code here\n```
- There should only be ONE explanation section, and ONE code block in the response.
- No other text should be included in the response.
- The function produced MUST be named `candidate`, or the test cases will fail.

**EXPLANATION RULES**
- The explanation should be no more than 3 sentences.
- The explanation should describe the code, the approach, and any important details.

**CODE RULES**
- The function should be a valid {PROGRAMMING_LANGUAGE} function.
- The function should be named `candidate`.
- The function should not contain any print statements.
- The function should contain explanatory comments.
- Only output a single function. If you are unsure, output the most universal version of the function.
- If subfunctions are needed, they should be defined inside the main function.
- No code should be outside the function.
- No test cases should be included in the code block.

See the below for the original prompt, the code that was generated, and the error message.

The original prompt is:

%%%PROMPT%%%

The code that was generated is:

```{PROGRAMMING_LANGUAGE}
%%%CODE%%%
```

The error message is:
```
%%%ERROR%%%
```

"""
