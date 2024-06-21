import os
import glob
import json
import numpy as np

# Path to the JSON files
path = "/ZPOOL/data/projects/sharedreward-aging/derivatives/mriqc/sub-*/func/*part-mag_bold.json"

# Find all JSON files
json_files = glob.glob(path)

# Lists to store participant IDs and corresponding fd_mean values
participants = []
fd_means = []

for file in json_files:
    # Extract the participant ID from the file path
    participant_id = os.path.basename(file).split('/')[0].split('-')[1]  # Extracting participant ID from path

    with open(file, 'r') as f:
        try:
            data = json.load(f)
            fd_mean_str = data.get('fd_mean')

            if fd_mean_str is not None:
                # Convert fd_mean from string to float
                fd_mean = float(fd_mean_str)

                # Append participant ID and fd_mean to lists
                participants.append(participant_id)
                fd_means.append(fd_mean)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing file {file}: {str(e)}")

# Print the results in tabular format
print("Participant ID\tfd_mean")
print("-----------------------------")
for i in range(len(participants)):
    print(f"{participants[i]}\t\t{fd_means[i]}")
