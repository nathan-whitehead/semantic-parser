import os
import json
import numpy as np
from collections import defaultdict

import matplotlib.pyplot as plt


def process_results(directory="output-llama3.2latest"):
  """
  Process JSON files in the specified directory to extract num_iterations and success.
  
  Args:
    directory (str): Directory containing JSON result files
  
  Returns:
    dict: Dictionary containing various statistics
  """
  # Initialize result storage
  results = {
    "num_iterations": [],
    "success": [],
    "successful_iterations": [],
    "failed_iterations": []
  }

  # Check if directory exists
  if not os.path.exists(directory):
    print(f"Error: Directory '{directory}' not found.")
    return results

  count = 0
  # Process each JSON file in the directory
  for filename in os.listdir(directory):
    if filename.endswith(".json"):
      count += 1
      print(f"Processing {count}", end="\r")
      filepath = os.path.join(directory, filename)
      try:
        with open(filepath, 'r') as file:
          data = json.load(file)

          # Extract required fields if they exist
          if "num_iterations" in data:
            results["num_iterations"].append(data["num_iterations"])

          if "success" in data:
            success = data["success"]
            results["success"].append(success)

            # Track iterations for successful and failed attempts separately
            if "num_iterations" in data:
              if success:
                results["successful_iterations"].append(data["num_iterations"])
              else:
                results["failed_iterations"].append(data["num_iterations"])
      except (json.JSONDecodeError, IOError) as e:
        print(f"Error processing file {filename}: {e}")

  return results


def generate_statistics(results):
  """
  Generate statistics from the processed results.
  
  Args:
    results (dict): Dictionary containing processed results
  
  Returns:
    dict: Dictionary containing statistics
  """
  stats = {}

  # Calculate basic statistics
  total_problems = len(results["success"])
  if total_problems > 0:
    successful_problems = sum(results["success"])
    stats["success_rate"] = successful_problems / total_problems
    stats["total_problems"] = total_problems
    stats["successful_problems"] = successful_problems

  # Calculate iteration statistics
  if results["num_iterations"]:
    stats["avg_iterations"] = np.mean(results["num_iterations"])
    stats["median_iterations"] = np.median(results["num_iterations"])
    stats["max_iterations"] = max(results["num_iterations"])
    stats["min_iterations"] = min(results["num_iterations"])

  # Calculate statistics for successful attempts
  if results["successful_iterations"]:
    stats["avg_successful_iterations"] = np.mean(results["successful_iterations"])
    stats["median_successful_iterations"] = np.median(results["successful_iterations"])

  # Calculate statistics for failed attempts
  if results["failed_iterations"]:
    stats["avg_failed_iterations"] = np.mean(results["failed_iterations"])
    stats["median_failed_iterations"] = np.median(results["failed_iterations"])

  return stats


def plot_results(results):
  """
  Create visualizations of the results.
  
  Args:
    results (dict): Dictionary containing processed results
  """
  # Create a figure with multiple subplots
  fig, axs = plt.subplots(2, 2, figsize=(15, 10))

  # Plot 1: Histogram of number of iterations
  # ** Change to only include successful iterations ** #
  if results["num_iterations"]:
    axs[0, 0].hist(
      results["num_iterations"], bins=max(5, min(20, max(results["num_iterations"])))
    )
    axs[0, 0].set_title("Distribution of Number of Iterations")
    axs[0, 0].set_xlabel("Number of Iterations")
    axs[0, 0].set_ylabel("Count")

  # Plot 2: Success rate
  if results["success"]:
    labels = ["Success", "Failure"]
    success_count = sum(results["success"])
    failure_count = len(results["success"]) - success_count
    axs[0, 1].pie([success_count, failure_count], labels=labels, autopct='%1.1f%%')
    axs[0, 1].set_title("Success Rate")

  # Plot 3: Comparison of iterations for successful vs failed attempts
  if results["successful_iterations"] and results["failed_iterations"]:
    labels = ["Successful", "Failed"]
    means = [
      np.mean(results["successful_iterations"]),
      np.mean(results["failed_iterations"])
    ]
    axs[1, 0].bar(labels, means)
    axs[1, 0].set_title("Average Iterations by Result")
    axs[1, 0].set_ylabel("Average Iterations")

  # Plot 4: Box plot of iterations
  data = [results["successful_iterations"], results["failed_iterations"]]
  if all(data):
    axs[1, 1].boxplot(data)
    axs[1, 1].set_xticklabels(["Successful", "Failed"])
    axs[1, 1].set_title("Iterations Distribution by Result")
    axs[1, 1].set_ylabel("Number of Iterations")

  plt.tight_layout()
  plt.savefig("results_analysis.png")
  plt.show()


if __name__ == "__main__":
  # Process all JSON files in the output directory
  results = process_results()

  # Generate and display statistics
  stats = generate_statistics(results)
  print("Results Statistics:")
  for key, value in stats.items():
    print(f"{key}: {value}")

  # Generate visualizations
  plot_results(results)

  print(f"\nProcessed {stats.get('total_problems', 0)} problems")
  print(f"Success rate: {stats.get('success_rate', 0)*100:.2f}%")
  print(f"Average iterations: {stats.get('avg_iterations', 0):.2f}")
