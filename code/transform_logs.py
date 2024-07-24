import glob
import pandas as pd
import re

# Define the input file pattern with a three-digit number
input_pattern = "/ZPOOL/data/projects/sharedreward-aging/ds003745/stimuli/psychopy/logs/*/sub*_SR-Ratings-*.csv"

# Define the new headers
new_headers = ['trial', 'partner', 'trait', 'ran', 'order', 'response']

# Function to check if the folder name contains exactly three digits
def is_three_digit_folder(path):
    match = re.search(r'/logs/(\d{3}/|\d{5}/)', path)
    return bool(match)

# Get the list of files matching the pattern
files = glob.glob(input_pattern)

# Filter files to include only those with a three-digit folder name
filtered_files = [file for file in files if is_three_digit_folder(file)]

# Iterate over each file and reformat the data
for file in filtered_files:
    # Read the CSV file
    df = pd.read_csv(file)
    
    # Update the headers
    df.columns = new_headers
    
    # Save the updated DataFrame back to the CSV file
    df.to_csv(file, index=False)

print("Data reformatting complete.")
