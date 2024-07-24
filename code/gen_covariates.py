import os
import glob
import pandas as pd

# Set pandas display options to show all rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Define the paths to the directories and files
logs_path = '/ZPOOL/data/projects/sharedreward-aging/ds003745/stimuli/psychopy/logs/'
participants_rf1_path = '/ZPOOL/data/projects/sharedreward-aging/ds003745/participants-rf1.tsv'
participants_srndna_path = '/ZPOOL/data/projects/sharedreward-aging/ds003745/participants-srndna.tsv'

# Find all CSV files in the directory and its subdirectories
all_files = glob.glob(os.path.join(logs_path, '**/sub*_SR-Ratings-2.csv'), recursive=True)

# List to hold individual dataframes
df_list = []

# Iterate over each file
for file in all_files:
    # Read the CSV file into a dataframe
    df = pd.read_csv(file)
    
    # Extract the subject number from the filename (assuming it follows the pattern subXXX)
    sub = os.path.basename(file).split('_')[0].replace('sub', '')
    
    # Add a new column for the subject number
    df['sub'] = sub
    
    # Append the dataframe to the list
    df_list.append(df)

# Concatenate all dataframes in the list into a single dataframe
combined_df = pd.concat(df_list, ignore_index=True)

# Read the participant files into dataframes
participants_rf1_df = pd.read_csv(participants_rf1_path, sep='\t')
participants_srndna_df = pd.read_csv(participants_srndna_path, sep='\t')

# Combine the participant dataframes into one
participants_df = pd.concat([participants_rf1_df, participants_srndna_df], ignore_index=True)

# Ensure sub and participant_id are of the same type
combined_df['sub'] = combined_df['sub'].astype(str)
participants_df['participant_id'] = participants_df['participant_id'].astype(str)

# Remove the 'sub-' prefix from the participant_id column
participants_df['participant_id'] = participants_df['participant_id'].str.replace('sub-', '')

# Merge the combined dataframe with the participants dataframe on the subject ID
combined_df = combined_df.merge(participants_df[['participant_id', 'age']], left_on='sub', right_on='participant_id', how='left')

# Drop the redundant 'participant_id' column
combined_df.drop(columns=['participant_id'], inplace=True)

# Print the shape of the combined dataframe
print("Shape of the combined dataframe:", combined_df.shape)

# Print the entire combined dataframe
print("Combined dataframe:")
print(combined_df)

# Output the combined dataframe to a new CSV file (optional)
# combined_df.to_csv('/ZPOOL/data/projects/sharedreward-aging/combined_data_with_age.csv', index=False)
