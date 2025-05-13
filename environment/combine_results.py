import os
import json


def combine_json_files(
  input_directory="output-llama3.2latest", output_file="combined_results.jsonl"
):
  """
    Combine all .json files in the specified directory into a single .jsonl file.

    Args:
        input_directory (str): Directory containing .json files.
        output_file (str): Path to the output .jsonl file.
    """
  if not os.path.exists(input_directory):
    print(f"Error: Directory '{input_directory}' not found.")
    return

  with open(output_file, 'w') as outfile:
    for filename in os.listdir(input_directory):
      print(f"Processing file: {filename}")
      if filename.endswith(".json"):
        filepath = os.path.join(input_directory, filename)
        try:
          with open(filepath, 'r') as infile:
            data = json.load(infile)
            outfile.write(json.dumps(data) + '\n')
        except (json.JSONDecodeError, IOError) as e:
          print(f"Error processing file {filename}: {e}")

  print(f"All JSON files combined into {output_file}")


if __name__ == "__main__":
  combine_json_files()
