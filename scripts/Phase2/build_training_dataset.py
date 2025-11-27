"""
This script builds a historical training dataset from archived JSON analyses.

It iterates through all .json files in the 'archived_analyses' directory,
extracts the Q-scores and the final match result, and compiles them into
a single CSV file for training the machine learning model.
"""
import os
import json
import pandas as pd
import glob

# Define the root directory for archived analyses and the output file
ARCHIVE_ROOT = "archived_analyses"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "training_dataset.csv")

def get_match_outcome(score: str) -> str:
    """Converts a score string 'H-A' into 'Home Win', 'Draw', or 'Away Win'."""
    if not score or '-' not in score:
        return None
    
    try:
        home_goals, away_goals = map(int, score.split('-'))
        if home_goals > away_goals:
            return "Home Win"
        if home_goals < away_goals:
            return "Away Win"
        return "Draw"
    except (ValueError, TypeError):
        return None

def extract_analysis_data(file_path: str) -> dict:
    """Extracts Q-scores and the outcome from a single analysis JSON file."""
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {file_path}")
            return None

    # Extract final score from the 'Betting Analysis' section
    final_score = data.get("Betting Analysis", {}).get("Match Result", {}).get("Full Time Score")
    
    # Alternative path for score if the first fails
    if not final_score:
        final_score = data.get("match_result", {}).get("ft_score")

    outcome = get_match_outcome(final_score)
    if not outcome:
        print(f"Warning: Could not determine outcome for {file_path}")
        return None

    # Extract Q-scores
    q_scores = data.get("Q-Scores")
    if not q_scores:
        print(f"Warning: No Q-Scores found in {file_path}")
        return None

    # Flatten the Q-scores into a single dictionary
    flat_scores = {f"Q{k}_Home": v.get('Home') for k, v in q_scores.items() if isinstance(v, dict)}
    flat_scores.update({f"Q{k}_Away": v.get('Away') for k, v in q_scores.items() if isinstance(v, dict)})
    
    flat_scores["outcome"] = outcome
    flat_scores["match_id"] = os.path.basename(file_path)

    return flat_scores

def build_dataset():
    """
    Main function to build and save the dataset.
    """
    # Ensure the output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Find all JSON files in the archive
    json_files = glob.glob(os.path.join(ARCHIVE_ROOT, "**", "*.json"), recursive=True)
    
    if not json_files:
        print(f"Error: No JSON files found in '{ARCHIVE_ROOT}'. Cannot build dataset.")
        return

    print(f"Found {len(json_files)} archived analysis files.")

    all_match_data = []
    for file in json_files:
        data = extract_analysis_data(file)
        if data:
            all_match_data.append(data)

    if not all_match_data:
        print("Error: No valid data could be extracted. Dataset will not be created.")
        return

    # Create DataFrame
    df = pd.DataFrame(all_match_data)

    # Reorder columns to have match_id and outcome first
    cols = ["match_id", "outcome"] + [col for col in df.columns if col not in ["match_id", "outcome"]]
    df = df[cols]

    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Successfully built dataset with {len(df)} records.")
    print(f"Dataset saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_dataset()
