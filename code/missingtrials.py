import os
import glob
import pandas as pd

# Directory containing the text files
base_dir = '/ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/EVfiles/sub-*/sharedreward/'

# Find all .txt files in the directory, excluding those with "block" in the filename
txt_files = [file for file in glob.glob(os.path.join(base_dir, '*.txt')) if 'block' not in os.path.basename(file)]

# Directory containing the missed trial text files for all subjects
missed_trial_dir = '/ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/EVfiles/sub-*/sharedreward/run-*_missed_trial.txt'
missed_trial_files = glob.glob(missed_trial_dir)

# Dictionary to store results
data = []

# Process each text file
for file_path in txt_files:
    with open(file_path, 'r') as file:
        content = file.read().strip()
        
    # Extract the subject number from the file path
    subject_number = os.path.basename(os.path.dirname(os.path.dirname(file_path))).replace('sub-', '')
    
    # Extract the filename and determine the run number
    filename = os.path.basename(file_path)
    filename_without_run = filename.replace('run-1_', '').replace('run-2_', '')
    run_number = '1' if 'run-1' in filename else '2' if 'run-2' in filename else 'unknown'
    
    if run_number != 'unknown':
        # Check the content and code it as 0 or 1
        data_code = 0 if content == '0 0 0' else 1
        
        # Append the results to the data list
        data.append([subject_number, run_number, filename_without_run, data_code])

# Initialize a dictionary to store missed trial counts
missed_trial_count_dict = {}

# Process each missed trial text file for all subjects
for missed_trial_path in missed_trial_files:
    # Extract the subject number from the file path
    subject_number = os.path.basename(os.path.dirname(os.path.dirname(missed_trial_path))).replace('sub-', '')
    
    # Determine the run number
    run_number = '1' if 'run-1' in missed_trial_path else '2' if 'run-2' in missed_trial_path else 'unknown'
    
    if run_number != 'unknown':
        # Read the missed trial file and count the number of rows
        with open(missed_trial_path, 'r') as file:
            missed_trial_count = len(file.readlines())
        
        # Store the missed trial count in the dictionary
        if subject_number not in missed_trial_count_dict:
            missed_trial_count_dict[subject_number] = {}
        missed_trial_count_dict[subject_number][run_number] = missed_trial_count

# Create a DataFrame from the data list
df = pd.DataFrame(data, columns=['Subject', 'Run', 'Filename', 'DataCode'])

# Pivot the DataFrame to have the filenames as columns and runs as rows
df_pivot = df.pivot_table(index=['Subject', 'Run'], columns='Filename', values='DataCode', fill_value=0).reset_index()

# Add the missed trial counts to the DataFrame
df_pivot['Missed_Trial_Count'] = df_pivot.apply(
    lambda row: missed_trial_count_dict.get(row['Subject'], {}).get(row['Run'], 0), axis=1
)

# Save the DataFrame to a CSV file
output_file = 'missing_trials_coding.csv'
df_pivot.to_csv(output_file, index=False)

print(f'Results saved to {output_file}')
