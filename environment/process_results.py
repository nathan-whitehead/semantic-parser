import os
import json
import numpy as np
from collections import defaultdict

import matplotlib.pyplot as plt


def process_results(jsonl_file="combined_results.jsonl"):
  """
    Process a .jsonl file to extract num_iterations and success.

    Args:
        jsonl_file (str): Path to the .jsonl file containing result data.

    Returns:
        dict: Dictionary containing various statistics.
    """
  # Initialize result storage
  results = {
    "num_iterations": [],
    "success": [],
    "successful_iterations": [],
    "failed_iterations": []
  }

  # Check if the .jsonl file exists
  if not os.path.exists(jsonl_file):
    print(f"Error: File '{jsonl_file}' not found.")
    return results

  try:
    with open(jsonl_file, 'r') as file:
      for line in file:
        try:
          data = json.loads(line)

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
        except json.JSONDecodeError as e:
          print(f"Error decoding line: {e}")
  except IOError as e:
    print(f"Error reading file {jsonl_file}: {e}")

  return results


def generate_statistics(results):
  """
    Generate statistics from the processed results, including proportions for one iteration and >1 iteration.
    
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

    # Proportions for one iteration and >1 iteration
    one_iteration_count = sum(1 for x in results["successful_iterations"] if x == 1)
    more_than_one_iteration_count = sum(
      1 for x in results["successful_iterations"] if x > 1
    )
    stats["proportion_one_iteration"] = one_iteration_count / len(
      results["successful_iterations"]
    )
    stats["proportion_more_than_one_iteration"] = more_than_one_iteration_count / len(
      results["successful_iterations"]
    )

  # Calculate statistics for failed attempts
  if results["failed_iterations"]:
    stats["avg_failed_iterations"] = np.mean(results["failed_iterations"])
    stats["median_failed_iterations"] = np.median(results["failed_iterations"])

  return stats


def plot_results(results):
  """
    Create visualizations of the results and save each chart as a separate .pdf file.
    
    Args:
        results (dict): Dictionary containing processed results
    """
  # Plot 1: Histogram of number of iterations (successful only)
  if results["successful_iterations"]:
    plt.figure(figsize=(8, 6))
    plt.hist(
      results["successful_iterations"],
      bins=max(5, min(20, max(results["successful_iterations"])))
    )
    plt.title("Distribution of Successful Iterations")
    plt.xlabel("Number of Iterations")
    plt.ylabel("Count")
    plt.savefig("successful_iterations_histogram.pdf", transparent=True)
    plt.close()

  # Plot 2: Success rate
  if results["success"]:
    plt.figure(figsize=(8, 6))
    labels = ["Success", "Failure"]
    success_count = sum(results["success"])
    failure_count = len(results["success"]) - success_count
    plt.pie([success_count, failure_count], labels=labels, autopct='%1.1f%%')
    plt.title("Success Rate")
    plt.savefig("success_rate_pie_chart.pdf", transparent=True)
    plt.close()

  # Plot 3: Comparison of iterations for successful vs failed attempts
  if results["successful_iterations"] and results["failed_iterations"]:
    plt.figure(figsize=(8, 6))
    labels = ["Successful", "Failed"]
    means = [
      np.mean(results["successful_iterations"]),
      np.mean(results["failed_iterations"])
    ]
    plt.bar(labels, means)
    plt.title("Average Iterations by Result")
    plt.ylabel("Average Iterations")
    plt.savefig("average_iterations_bar_chart.pdf", transparent=True)
    plt.close()

  # Plot 4: Box plot of iterations
  data = [results["successful_iterations"], results["failed_iterations"]]
  if all(data):
    plt.figure(figsize=(8, 6))
    plt.boxplot(data)
    plt.xticks([1, 2], ["Successful", "Failed"])
    plt.title("Iterations Distribution by Result")
    plt.ylabel("Number of Iterations")
    plt.savefig("iterations_distribution_box_plot.pdf", transparent=True)
    plt.close()


if __name__ == "__main__":
  # Combine JSON files into a single .jsonl file (optional, if not already done)
  # Uncomment the following line if you want to combine files before processing
  # combine_json_files()

  # Process the combined .jsonl file
  print("Processing results")
  results = process_results("combined_results.jsonl")

  # Generate and display statistics
  print("Generating statistics")
  stats = generate_statistics(results)
  print("Results Statistics:")
  for key, value in stats.items():
    print(f"{key}: {value}")

  # Generate visualizations
  print("Generating visualizations")
  plot_results(results)

  print(f"\nProcessed {stats.get('total_problems', 0)} problems")
  print(f"Success rate: {stats.get('success_rate', 0)*100:.2f}%")
  print(f"Average iterations: {stats.get('avg_iterations', 0):.2f}")
  print(
    f"Proportion of cases with one iteration: {stats.get('proportion_one_iteration', 0)*100:.2f}%"
  )
  print(
    f"Proportion of cases with >1 iteration: {stats.get('proportion_more_than_one_iteration', 0)*100:.2f}%"
  )
