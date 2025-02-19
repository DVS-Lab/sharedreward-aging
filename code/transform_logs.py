import glob
import pandas as pd
import os
import re

# Define the input file pattern
input_pattern = "/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging/stimuli/logs/*/sub*_SR-Ratings-*.csv"

# Define the new base directory for reformatted files
output_base_dir = "/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging/stimuli/logs-reformatted/"

# Define the new headers
new_headers = ['trial', 'partner', 'trait', 'ran', 'order', 'response']

# Function to check if the folder name contains exactly three or five digits
def is_valid_folder(path):
    match = re.search(r'/logs/(\d{3}|\d{5})/', path)
    return bool(match)

# Get the list of files matching the pattern
files = glob.glob(input_pattern)

# Filter files to include only those with a valid folder name
filtered_files = [file for file in files if is_valid_folder(file)]

# Process each file
for file in filtered_files:
    # Read the CSV file
    df = pd.read_csv(file)
    
    # Update the headers
    df.columns = new_headers
    
    # Construct the new output path
    relative_path = os.path.relpath(file, "/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging/stimuli/logs/")
    new_file_path = os.path.join(output_base_dir, relative_path)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
    
    # Save the updated DataFrame to the new file location
    df.to_csv(new_file_path, index=False)
    
    print(f"Saved reformatted file to: {new_file_path}")

print("Data reformatting complete.")

