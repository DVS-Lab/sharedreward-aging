import os
import glob
import pandas as pd

# Path to the TSV files
path = "/ZPOOL/data/projects/sharedreward-aging/derivatives/fmriprep/sub-*/func/*_desc-confounds_timeseries.tsv"

# Find all TSV files
tsv_files = glob.glob(path)

# Dictionary to store participant IDs and their respective runs' averages
participant_averages = {}

for file in tsv_files:
    # Extract the participant ID and run number from the file name
    file_name = os.path.basename(file)
    participant_id = file_name.split('_')[0].split('-')[1]  # Extracting participant ID from path
    run_number = file_name.split('_')[2].split('-')[1]  # Extracting run number from path

    # Read the TSV file using pandas
    try:
        df = pd.read_csv(file, delimiter='\t')

        # Extract framewise_displacement column
        fd_column = df['framewise_displacement']

        # Calculate average framewise_displacement for the current run
        avg_fd = fd_column.mean()

        # Store the average in participant_averages dictionary
        if participant_id not in participant_averages:
            participant_averages[participant_id] = {}

        participant_averages[participant_id][run_number] = avg_fd

    except (pd.errors.EmptyDataError, KeyError, IndexError) as e:
        print(f"Error processing file {file}: {str(e)}")

# Print the results in tabular format
print("Participant ID\tRun Number\tAverage fd_mean")
print("---------------------------------------------")
for participant_id, runs in participant_averages.items():
    for run_number, avg_fd in runs.items():
        print(f"{participant_id}\t\t{run_number}\t\t{avg_fd}")
